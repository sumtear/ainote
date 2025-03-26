<template>
  <div class="note-add-page">
    <!-- 上部分 -->
    <div class="header">
      <el-button @click="goBack">
        <el-icon>
          <ArrowLeft />
        </el-icon>
      </el-button>
      <div class="title">编辑笔记</div>
      <el-button class="finish-button" type="primary" @click="finishNote"
        :disabled="noteTitle.length === 0">完成</el-button>
    </div>

    <!-- 中间部分编辑区 -->
    <div class="editor-container">
      <el-input v-model="noteTitle" placeholder="请输入标题" class="title-input"></el-input>

      <div class="content-editor">
        <QuillEditor class="quillEditorChild" ref="quillEditor" v-model="contentArea" @input="change"></QuillEditor>
      </div>

      <!-- 添加思维导图显示区域 -->
      <div v-if="mindmapImage" class="mindmap-container">
        <p>思维导图预览：</p>
        <img :src="'data:image/png;base64,' + mindmapImage" alt="思维导图" class="mindmap-image" />
      </div>
    </div>

    <!-- 下部分区 -->
    <div class="bottom-toolbar">
      <el-button icon="el-icon-back" @click="undo" class="toolbar-button"></el-button>
      <el-button icon="el-icon-right" @click="redo" class="toolbar-button"></el-button>

      <el-button icon="el-icon-plus" @click="toggleAddMenu" class="toolbar-button add-button"
        ref="addButton"></el-button>
    </div>

    <!-- 弹出层 -->
    <el-dialog v-model="addMenuVisible" width="80vw" :show-close="false" custom-class="custom-add-menu" :modal="false">
      <div class="add-menu-scroll-container">
        <div class="add-menu-content">
          <!-- 添加思维导图生成功能 -->
          <div class="add-menu-item" @click="generateMindmap">
            <div class="icon-container">
              <el-button class="icon-button">
                <i class="el-icon-connection"></i>
              </el-button>
            </div>
            <div class="text-container">生成思维导图</div>
          </div>

          <!-- 其他功能 -->
          <div class="add-menu-item">
            <div class="icon-container">
              <el-button class="icon-button">
                <i class="el-icon-microphone"></i>
              </el-button>
            </div>
            <div class="text-container">占位功能1</div>
          </div>
          <div class="add-menu-item">
            <div class="icon-container">
              <el-button class="icon-button">
                <i class="el-icon-tickets"></i>
              </el-button>
            </div>
            <div class="text-container">占位功能2</div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 加载中提示 -->
    <el-dialog v-model="loading" title="处理中" width="30%" :show-close="false">
      <div class="loading-content">
        <el-progress type="circle" :percentage="loadingProgress"></el-progress>
        <p>正在生成思维导图，请稍候...</p>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import QuillEditor from './QuillEditor.vue';
import { ArrowLeft } from '@element-plus/icons-vue'; // 引入图标
import axios from 'axios'; // 确保已安装axios

export default {
  name: 'NoteAdd',
  components: {
    QuillEditor,
    ArrowLeft,
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const quillEditor = ref(null);

    const noteId = ref(Number(route.query.id) || 0);
    const userId = ref(1); // 假设当前用户ID为1，实际应从用户登录信息中获取
    const noteTitle = ref('');
    const contentArea = ref('');
    const addMenuVisible = ref(false);
    const loading = ref(false);
    const loadingProgress = ref(0);
    const mindmapImage = ref('');
    const mindmapPath = ref('');

    // 返回上一页
    const goBack = () => {
      router.push('/');
    };

    // 撤销操作
    const undo = () => {
      if (quillEditor.value) {
        const quill = quillEditor.value.getQuillInstance();
        if (quill) {
          quill.history.undo();
        }
      }
    };

    // 重做操作
    const redo = () => {
      if (quillEditor.value) {
        const quill = quillEditor.value.getQuillInstance();
        if (quill) {
          quill.history.redo();
        }
      }
    };

    // 生成思维导图
    const generateMindmap = async () => {
      const content = getEditorContent();
      if (!content) {
        ElMessage.warning('请先输入笔记内容');
        return;
      }

      // 关闭菜单
      addMenuVisible.value = false;

      // 显示加载提示
      loading.value = true;
      loadingProgress.value = 0;

      // 定时增加加载进度
      const progressInterval = setInterval(() => {
        loadingProgress.value += 10;
        if (loadingProgress.value >= 90) {
          clearInterval(progressInterval);
        }
      }, 1000);

      try {
        // 提取文本内容(移除HTML标签)
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        const text = tempDiv.textContent || tempDiv.innerText || '';

        console.log(text);

        // 调用后端API生成思维导图
        const response = await axios.post('/generate-mindmap', {
          text: text,
          user_id: userId.value,
          save_as_note: false, // 此处先不保存为笔记，在完成时统一保存
          title: noteTitle.value || '新建笔记'
        });

        clearInterval(progressInterval);

        if (response.data.success) {
          // 显示生成的思维导图
          mindmapImage.value = response.data.mindmap_image;
          mindmapPath.value = response.data.mindmap_path;

          ElMessage.success('思维导图生成成功');
          loadingProgress.value = 100;
        } else {
          ElMessage.error('生成思维导图失败: ' + response.data.error);
        }
      } catch (error) {
        ElMessage.error('请求错误: ' + (error.response?.data?.error || error.message));
      } finally {
        clearInterval(progressInterval);
        loading.value = false;
      }
    };

    const getEditorContent = () => {
      if (quillEditor.value) {
        const quill = quillEditor.value.getQuillInstance();
        if (quill) {
          // 获取HTML内容
          return quill.root.innerHTML;
        }
      }
      return contentArea.value; // 回退到模型绑定的值
    };

    const finishNote = async () => {
      try {
        const title = noteTitle.value.trim();
        if (!title) {
          ElMessage.warning('请输入笔记标题');
          return;
        }
        // 确保内容正确获取
        const content = getEditorContent();

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        const text = tempDiv.textContent || tempDiv.innerText || '';
        console.log('发送的笔记内容:', text); // 调试日志

        let url, method;
        const noteData = {
          title: title,
          content: text,
          user_id: userId.value
        };

        // 如果有思维导图，保存路径
        if (mindmapPath.value) {
          noteData.image = mindmapPath.value;
        }

        console.log('发送的完整数据:', noteData); // 调试日志

        // 根据是新建还是编辑决定API调用
        if (noteId.value) {
          // 更新现有笔记
          url = `/api/notes/${noteId.value}`;
          method = 'put';
        } else {
          // 创建新笔记
          url = '/api/notes';
          method = 'post';
        }

        // 使用更详细的错误处理和日志记录
        const response = await axios({
          method: method,
          url: url,
          data: noteData,
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 10000 // 10秒超时
        });

        console.log('后端响应:', response.data); // 调试日志

        if (response.data.success) {
          ElMessage.success(noteId.value ? '笔记更新成功' : '笔记创建成功');
          goBack();
        } else {
          ElMessage.error('操作失败: ' + (response.data.error || '未知错误'));
        }
      } catch (error) {
        console.error('请求错误详情:', error);

        if (error.response) {
          // 服务器响应了，但状态码不在2xx范围
          console.error('错误响应状态:', error.response.status);
          console.error('错误响应数据:', error.response.data);
          ElMessage.error(`请求失败(${error.response.status}): ${error.response.data.error || '服务器错误'}`);
        } else if (error.request) {
          // 请求发出，但没有收到响应
          console.error('无响应错误:', error.request);
          ElMessage.error('服务器没有响应，请检查网络连接');
        } else {
          // 设置请求时发生错误
          console.error('请求设置错误:', error.message);
          ElMessage.error('请求错误: ' + error.message);
        }
      }
    };

    // 切换添加菜单
    const toggleAddMenu = () => {
      addMenuVisible.value = !addMenuVisible.value;
    };

    // 内容变化事件
    const change = (event) => {
      console.log('更新值:', event);
    };

    // 加载编辑笔记
    const loadEditNote = async () => {
      if (!noteId.value) return;

      try {
        const response = await axios.get(`/api/notes/${noteId.value}`);
        if (response.data.success) {
          const note = response.data.note;
          noteTitle.value = note.title;
          contentArea.value = note.content;

          // 如果有思维导图，加载预览
          if (note.image && note.image.startsWith('static/mindmaps/')) {
            try {
              const imageResponse = await axios.get(`/mindmap-images/${note.image.split('/').pop()}`,
                { responseType: 'arraybuffer' });

              const base64 = btoa(
                new Uint8Array(imageResponse.data)
                  .reduce((data, byte) => data + String.fromCharCode(byte), '')
              );
              mindmapImage.value = base64;
              mindmapPath.value = note.image;
            } catch (imgError) {
              console.error('加载思维导图图片失败', imgError);
            }
          }
        } else {
          ElMessage.error('加载笔记失败: ' + response.data.error);
        }
      } catch (error) {
        ElMessage.error('请求错误: ' + (error.response?.data?.error || error.message));
      }
    };

    // 初始化
    onMounted(() => {
      loadEditNote();
    });

    return {
      noteId,
      noteTitle,
      contentArea,
      addMenuVisible,
      loading,
      loadingProgress,
      mindmapImage,
      quillEditor,
      goBack,
      undo,
      redo,
      finishNote,
      toggleAddMenu,
      generateMindmap,
      change
    };
  }
};
</script>

<style scoped>
.note-add-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f5f5f5;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
  height: 10%;
}

.title {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
}

.finish-button {
  margin-left: 10px;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  overflow-y: auto;
  height: 80%;
}

.title-input {
  margin-bottom: 10px;
}

.content-editor {
  flex: 1;
}

/* 添加思维导图样式 */
.mindmap-container {
  margin-top: 20px;
  padding: 10px;
  border: 1px dashed #ccc;
  border-radius: 5px;
}

.mindmap-image {
  max-width: 100%;
  height: auto;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.bottom-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: #f5f5f5;
  box-shadow: 0 -1px 5px rgba(0, 0, 0, 0.1);
  height: 10%;
}

.add-menu-scroll-container {
  display: flex;
  overflow-x: auto;
  white-space: nowrap;
  padding: 10px;
}

.add-menu-content {
  display: flex;
  align-items: center;
}

.add-menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 10px;
  cursor: pointer;
}

.icon-container {
  margin-bottom: 4px;
}

.text-container {
  text-align: center;
}

.custom-add-menu .el-dialog__header {
  display: none;
}

.custom-add-menu .el-dialog__body {
  padding: 0;
}

.custom-add-menu .el-dialog {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  margin-top: -10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}
</style>