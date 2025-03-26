<template>
  <div class="note-page">
    <!-- 上部分 -->
    <div class="header">
      <div class="title">简易笔记</div>
      <div class="actions">
        <el-button circle @click="showSearchDialog = true">
          <el-icon>
            <Search />
          </el-icon>
        </el-button>
        <el-button circle @click="addNote">
          <el-icon>
            <Plus />
          </el-icon>
        </el-button>
      </div>
    </div>

    <!-- 中间内容区 -->
    <div class="content">
      <!-- 添加加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else-if="filteredNotes.length !== 0">
        <el-card v-for="note in filteredNotes" :key="note.id" class="note-card">
          <div class="note-content">
            <div class="note-main" @click="editNote(note)">
              <h3 class="note-title">{{ note.title }}</h3>
              <p class="note-summary">{{ generatePreview(note.content) }}</p>
              <p class="note-time">{{ formatDate(note.update_time || note.create_time) }}</p>
              <!-- 如果有思维导图则显示标签 -->
              <el-tag v-if="note.image" size="small" type="success" class="note-tag">思维导图</el-tag>
            </div>
            <div class="note-delete">
              <el-button type="danger" @click.stop="deleteNote(note)" class="delete-button">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
      <div v-else class="note-no-content">
        暂未新建笔记
      </div>
    </div>

    <!-- 下部分菜单栏 -->
    <div class="footer">
      <el-menu mode="horizontal" class="footer-menu" :default-active="currentMenuItem" @select="handleMenuSelect">
        <el-menu-item index="1">笔记</el-menu-item>
        <el-menu-item index="2">我的</el-menu-item>
      </el-menu>
    </div>

    <!-- 弹出层 -->
    <el-dialog title="检索笔记" v-model="showSearchDialog" width="100%" :fullscreen="false" class="search-dialog"
      :before-close="handleClose">
      <div class="dialog-content">
        <div class="input-container">
          <el-input v-model="searchQuery" placeholder="请输入标题关键字" clearable @input="filterNotes"></el-input>
        </div>
        &nbsp;
        <div class="button-container">
          <el-button type="primary" @click="showSearchDialog = false">确认</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';
import { Search, Plus, Delete } from '@element-plus/icons-vue';
import axios from 'axios';

export default {
  name: 'NoteApp',
  components: {
    Search,
    Plus,
    Delete
  },
  setup() {
    const router = useRouter();
    const currentMenuItem = ref('1');
    const notes = ref([]);
    const showSearchDialog = ref(false);
    const searchQuery = ref('');
    const filteredNotes = ref([]);
    const loading = ref(false);

    // 假设从登录信息或本地存储获取用户ID
    const userId = ref(localStorage.getItem('userId') || 1);

    // 从后端API获取所有笔记
    const getAllNotes = async () => {
      loading.value = true;
      try {
        // 调用后端API获取笔记数据
        const response = await axios.get(`/api/notes?user_id=${userId.value}`);

        if (response.data && response.data.success) {
          // 获取成功
          notes.value = response.data.notes || [];
          console.log('获取到的笔记数据:', notes.value);
        } else {
          // 获取失败
          ElMessage.error('获取笔记列表失败: ' + (response.data?.error || '未知错误'));
          notes.value = [];
        }
      } catch (error) {
        console.error('获取笔记出错:', error);
        ElMessage.error('获取笔记失败，请检查网络连接或服务器状态');
        notes.value = [];
      } finally {
        loading.value = false;
      }
    };

    // 生成预览文本，从HTML内容中提取纯文本
    const generatePreview = (content, maxLength = 50) => {
      if (!content) return '无内容';

      try {
        // 移除HTML标签
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        let plainText = tempDiv.textContent || tempDiv.innerText || '';

        // 截取指定长度
        if (plainText.length > maxLength) {
          plainText = plainText.substring(0, maxLength) + '...';
        }

        return plainText || '无内容';
      } catch (error) {
        console.error('预览生成错误', error);
        return '内容预览错误';
      }
    };

    // 格式化日期显示
    const formatDate = (dateStr) => {
      if (!dateStr) return '未知时间';

      try {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
          // 今天 - 显示时间
          return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        } else if (diffDays === 1) {
          return '昨天';
        } else if (diffDays < 7) {
          return `${diffDays}天前`;
        } else {
          // 超过一周 - 显示完整日期
          return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
        }
      } catch (error) {
        console.error('日期格式化错误', error);
        return dateStr;
      }
    };

    // 过滤笔记
    const filterNotes = () => {
      if (!notes.value || notes.value.length === 0) {
        filteredNotes.value = [];
        return;
      }

      if (searchQuery.value.trim() === '') {
        filteredNotes.value = notes.value;
      } else {
        const query = searchQuery.value.toLowerCase();
        filteredNotes.value = notes.value.filter(note => {
          const titleMatch = note.title && note.title.toLowerCase().includes(query);
          const contentMatch = note.content && generatePreview(note.content).toLowerCase().includes(query);
          return titleMatch || contentMatch;
        });
      }
    };

    // 删除笔记
    const deleteNote = (note) => {
      ElMessageBox.confirm('确认删除?', '确认信息', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        center: true
      }).then(async () => {
        try {
          loading.value = true;
          // 调用API删除笔记
          const response = await axios.delete(`/api/notes/${note.id}`);

          if (response.data && response.data.success) {
            ElMessage.success('删除成功');
            getAllNotes(); // 重新加载笔记列表
          } else {
            ElMessage.error('删除失败: ' + (response.data?.error || '未知错误'));
            loading.value = false;
          }
        } catch (error) {
          console.error('删除失败:', error);
          ElMessage.error('删除失败，请重试');
          loading.value = false;
        }
      }).catch(() => {
        console.log("取消删除");
      });
    };

    // 关闭搜索对话框
    const handleClose = (done) => {
      showSearchDialog.value = false;
      if (done) done();
    };

    // 添加笔记
    const addNote = () => {
      router.push({ path: '/noteAdd' });
    };

    // 编辑笔记
    const editNote = (note) => {
      router.push({ path: '/noteAdd2', query: { id: note.id } });
    };

    // 处理菜单选择
    const handleMenuSelect = (index) => {
      currentMenuItem.value = index;
      if (index === '2') {
        router.push('/user');  // 跳转到用户页面
      }
    };

    // 初始化
    onMounted(() => {
      getAllNotes();
    });

    // 监听 notes 和 searchQuery 的变化
    watch(notes, filterNotes);
    watch(searchQuery, filterNotes);

    return {
      currentMenuItem,
      notes,
      showSearchDialog,
      searchQuery,
      filteredNotes,
      loading,
      generatePreview,
      formatDate,
      filterNotes,
      deleteNote,
      handleClose,
      addNote,
      editNote,
      handleMenuSelect
    };
  }
};
</script>

<style scoped>
.note-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f7fa;
}

.header,
.footer {
  background-color: #f5f5f5;
  padding: 10px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.actions el-button {
  margin-left: 10px;
}

.loading-container {
  padding: 16px;
}

.content {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.note-card {
  margin-bottom: 10px;
  transition: transform 0.2s;
}

.note-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.note-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-no-content {
  font-weight: bold;
  text-align: center;
  margin-top: 100px;
  color: #909399;
}

.note-main {
  flex: 0 0 80%;
  cursor: pointer;
}

.note-delete {
  flex: 0 0 20%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.delete-button {
  width: 60px;
  height: 40px;
}

.note-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.note-summary {
  margin: 5px 0;
  color: #606266;
  line-height: 1.4;
}

.note-time {
  font-size: 12px;
  color: #888;
  margin: 3px 0;
}

.note-tag {
  margin-top: 5px;
}

.footer {
  background-color: #fff;
  padding: 10px;
}

.footer-menu {
  text-align: center;
}

.footer-menu .el-menu-item {
  line-height: 40px;
}

.search-dialog .dialog-content {
  display: flex;
  align-items: center;
}

.search-dialog .input-container {
  flex: 0 0 80%;
}

.search-dialog .button-container {
  flex: 0 0 20%;
}

.search-dialog .el-button {
  width: 100%;
}
</style>