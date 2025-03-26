<template>
  <div class="note-add-page">
    <!-- 上部分 -->
    <div class="header">
      <el-button class="back-button" @click="goBack">
        <el-icon>
          <ArrowLeft />
        </el-icon>
      </el-button>
      <div class="title">{{ noteId ? '编辑笔记' : '新建笔记' }}</div>
      <el-button class="finish-button" type="primary" @click="finishNote" :loading="saving"
        :disabled="!noteTitle || saving">完成</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 中间部分编辑区 -->
    <div v-else class="editor-container">
      <el-input v-model="noteTitle" placeholder="请输入标题" class="title-input" maxlength="100" show-word-limit></el-input>

      <div class="content-editor">
        <QuillEditor class="quillEditorChild" ref="quillEditor" v-model="contentArea" @contentData="change($event)">
        </QuillEditor>
      </div>

      <!-- 思维导图预览 -->
      <div v-if="mindmapUrl" class="mindmap-preview">
        <div class="mindmap-title">
          <span>思维导图预览</span>
          <el-button type="text" @click="regenerateMindmap" :loading="generatingMap">
            重新生成
          </el-button>
        </div>
        <el-image :src="mindmapUrl" fit="contain" :preview-src-list="[mindmapUrl]" class="mindmap-image">
          <template #error>
            <div class="mindmap-error">
              <el-icon>
                <PictureRounded />
              </el-icon>
              <div>思维导图加载失败</div>
            </div>
          </template>
        </el-image>
      </div>
    </div>

    <!-- 下部分工具栏 -->
    <div class="bottom-toolbar">
      <div class="toolbar-left">
        <el-button @click="undo" class="toolbar-button">
          <el-icon>
            <Back />
          </el-icon>
        </el-button>
        <el-button @click="redo" class="toolbar-button">
          <el-icon>
            <Right />
          </el-icon>
        </el-button>
      </div>

      <div class="toolbar-center">
        <el-button @click="toggleAddMenu" class="toolbar-button add-button" ref="addButton">
          <el-icon>
            <Plus />
          </el-icon>
        </el-button>
      </div>

      <div class="toolbar-right">
        <el-button @click="generateMindmap" class="toolbar-button" :loading="generatingMap" type="primary" plain>
          <el-icon>
            <Connection />
          </el-icon>
          思维导图
        </el-button>
      </div>
    </div>

    <!-- 插入内容菜单 -->
    <el-dialog v-model="addMenuVisible" title="插入内容" width="90%" destroy-on-close>
      <div class="add-menu-content">
        <!-- 图片 -->
        <el-card class="add-menu-item" shadow="hover" @click="insertImage">
          <template #header>
            <el-icon>
              <Picture />
            </el-icon>
          </template>
          <div class="text-container">插入图片</div>
        </el-card>

        <!-- 声音 -->
        <el-card class="add-menu-item" shadow="hover" @click="insertAudio">
          <template #header>
            <el-icon>
              <Microphone />
            </el-icon>
          </template>
          <div class="text-container">插入声音</div>
        </el-card>

        <!-- 文件 -->
        <el-card class="add-menu-item" shadow="hover" @click="insertFile">
          <template #header>
            <el-icon>
              <Document />
            </el-icon>
          </template>
          <div class="text-container">插入文件</div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import QuillEditor from './QuillEditor.vue';
import Quill from 'quill';
import axios from 'axios';
import {
  ArrowLeft, Back, Right, Plus, Picture,
  Microphone, Document, Connection, PictureRounded
} from '@element-plus/icons-vue';

export default {
  name: 'NoteAdd2',
  components: {
    QuillEditor,
    ArrowLeft,
    Back,
    Right,
    Plus,
    Picture,
    Microphone,
    Document,
    Connection,
    PictureRounded
  },
  setup() {
    const router = useRouter();
    const route = useRoute();

    const noteId = ref(route.query.id ? Number(route.query.id) : null);
    const noteTitle = ref('');
    const contentArea = ref('');
    const addMenuVisible = ref(false);
    const insertIndex = ref(0);
    const quillEditor = ref(null);
    const loading = ref(false);
    const saving = ref(false);
    const mindmapUrl = ref('');
    const generatingMap = ref(false);

    // 假设从登录信息或本地存储获取用户ID
    const userId = ref(localStorage.getItem('userId') || 1);

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

    // 从后端加载笔记内容
    const loadNoteContent = async () => {
      if (!noteId.value) return;

      loading.value = true;
      try {
        const response = await axios.get(`/api/notes/${noteId.value}`);

        if (response.data && response.data.success) {
          const noteData = response.data.note;
          noteTitle.value = noteData.title || '';
          console.log('noteData:', noteData);
          const content = noteData.content || '';
          contentArea.value = content;

          // 等待DOM更新后再设置编辑器内容
          await nextTick();

          console.log('quillEditor引用:', quillEditor.value);
          const quill = quillEditor.value?.getQuillInstance();
          console.log('quill实例:', quill);
          if (quill) {
            console.log('设置内容前:', quill.root.innerHTML);
            quill.root.innerHTML = noteData.content || '';
            console.log('设置内容后:', quill.root.innerHTML);
          } else {
            console.error('获取Quill实例失败');
          }

          // 如果有思维导图，加载思维导图URL
          if (noteData.image) {
            const baseUrl = process.env.NODE_ENV === 'production'
              ? window.location.origin
              : 'http://localhost:5000';

            mindmapUrl.value = noteData.image.startsWith('http')
              ? noteData.image
              : `${baseUrl}/${noteData.image}`;
          }

          console.log('笔记加载成功:', noteData.title);
        } else {
          ElMessage.error('加载笔记失败: ' + (response.data?.error || '未知错误'));
        }
      } catch (error) {
        console.error('加载笔记出错:', error);
        ElMessage.error('加载笔记失败，请检查网络连接');
      } finally {
        loading.value = false;
      }
    };

    // 返回上一页
    const goBack = () => {
      if (hasContentChanged()) {
        ElMessageBox.confirm('内容已修改但未保存，确定要离开吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          router.push('/');
        }).catch(() => { });
      } else {
        router.push('/');
      }
    };

    // 检查内容是否已修改
    const hasContentChanged = () => {
      // 如果是新笔记，检查标题或内容是否有输入
      if (!noteId.value) {
        return noteTitle.value.trim() !== '' ||
          (quillEditor.value?.getQuillInstance().getText().trim() !== '');
      }

      // TODO: 对于编辑现有笔记，可以与原始内容比较
      // 简化处理，假设有修改
      return true;
    };

    // 撤销操作
    const undo = () => {
      const quill = quillEditor.value?.getQuillInstance();
      if (quill) {
        quill.history.undo();
      }
    };

    // 重做操作
    const redo = () => {
      const quill = quillEditor.value?.getQuillInstance();
      if (quill) {
        quill.history.redo();
      }
    };

    // 完成笔记（保存到后端）
    const finishNote = async () => {
      if (!noteTitle.value.trim()) {
        ElMessage.warning('请输入笔记标题');
        return;
      }

      saving.value = true;
      try {
        const quill = quillEditor.value.getQuillInstance();
        const html = quill.root.innerHTML;

        const noteData = {
          title: noteTitle.value.trim(),
          content: html,
          user_id: userId.value
        };

        // 如果存在思维导图，也一并保存
        if (mindmapUrl.value) {
          noteData.image = mindmapUrl.value.split('/').pop(); // 只保存文件名部分
        }

        let response;
        if (noteId.value) {
          // 更新现有笔记
          response = await axios.put(`/api/notes/${noteId.value}`, noteData);
        } else {
          // 创建新笔记
          response = await axios.post('/api/notes', noteData);
        }

        if (response.data && response.data.success) {
          ElMessage.success(noteId.value ? '笔记更新成功' : '笔记创建成功');
          router.push('/');
        } else {
          ElMessage.error('保存失败: ' + (response.data?.error || '未知错误'));
        }
      } catch (error) {
        console.error('保存笔记出错:', error);
        ElMessage.error('保存笔记失败，请重试');
      } finally {
        saving.value = false;
      }
    };

    // 切换添加菜单
    const toggleAddMenu = () => {
      const quill = quillEditor.value?.getQuillInstance();
      if (quill) {
        const selection = quill.getSelection();
        if (selection) {
          insertIndex.value = selection.index;
        }
        addMenuVisible.value = !addMenuVisible.value;
      }
    };

    // 插入图片
    const insertImage = () => {
      const quill = quillEditor.value?.getQuillInstance();
      if (!quill) return;

      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';

      input.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
          try {
            // 创建FormData对象
            const formData = new FormData();
            formData.append('image', file);

            // 上传图片到服务器
            const response = await axios.post('/api/upload_image', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });

            if (response.data && response.data.success) {
              const imageURL = response.data.url;
              const range = quill.getSelection();
              const index = range ? range.index : insertIndex.value || quill.getLength();

              // 插入图片并添加换行
              quill.insertEmbed(index, 'image', imageURL, Quill.sources.USER);
              quill.insertText(index + 1, '\n', Quill.sources.USER);
              quill.setSelection(index + 2, Quill.sources.SILENT);

              ElMessage.success('图片插入成功');
            } else {
              ElMessage.error('图片上传失败: ' + (response.data?.error || '未知错误'));
            }
          } catch (error) {
            console.error('上传图片出错:', error);
            ElMessage.error('图片上传失败，请重试');
          }
        }
      });

      input.click();
      addMenuVisible.value = false;
    };

    // 插入音频
    const insertAudio = () => {
      const quill = quillEditor.value?.getQuillInstance();
      if (!quill) return;

      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'audio/*';

      input.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
          try {
            // 创建FormData对象
            const formData = new FormData();
            formData.append('audio', file);

            // 上传音频到服务器
            const response = await axios.post('/api/upload_audio', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });

            if (response.data && response.data.success) {
              const audioURL = response.data.url;
              const range = quill.getSelection();
              const index = range ? range.index : insertIndex.value || quill.getLength();

              // 创建音频控件
              const audioElement = `<audio controls src="${audioURL}"></audio><p></p>`;
              quill.clipboard.dangerouslyPasteHTML(index, audioElement, Quill.sources.USER);
              quill.setSelection(index + 1, Quill.sources.SILENT);

              ElMessage.success('音频插入成功');
            } else {
              ElMessage.error('音频上传失败: ' + (response.data?.error || '未知错误'));
            }
          } catch (error) {
            console.error('上传音频出错:', error);
            ElMessage.error('音频上传失败，请重试');
          }
        }
      });

      input.click();
      addMenuVisible.value = false;
    };

    // 插入文件
    const insertFile = () => {
      const quill = quillEditor.value?.getQuillInstance();
      if (!quill) return;

      const input = document.createElement('input');
      input.type = 'file';

      input.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
          try {
            // 创建FormData对象
            const formData = new FormData();
            formData.append('file', file);

            // 上传文件到服务器
            const response = await axios.post('/api/upload_file', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });

            if (response.data && response.data.success) {
              const fileURL = response.data.url;
              const fileName = response.data.fileName || file.name;
              const range = quill.getSelection();
              const index = range ? range.index : insertIndex.value || quill.getLength();

              // 插入文件链接
              quill.insertText(index, `文件: ${fileName} `, Quill.sources.USER);
              quill.insertText(index + `文件: ${fileName} `.length, '下载', 'link', fileURL);
              quill.insertText(index + `文件: ${fileName} 下载`.length, '\n', Quill.sources.USER);

              ElMessage.success('文件插入成功');
            } else {
              ElMessage.error('文件上传失败: ' + (response.data?.error || '未知错误'));
            }
          } catch (error) {
            console.error('上传文件出错:', error);
            ElMessage.error('文件上传失败，请重试');
          }
        }
      });

      input.click();
      addMenuVisible.value = false;
    };

    // 生成思维导图
    const generateMindmap = async () => {
      if (generatingMap.value) return;

      const quill = quillEditor.value?.getQuillInstance();
      if (!quill) return;

      const content = quill.getText();
      if (!content || content.trim().length < 10) {
        ElMessage.warning('内容太少，无法生成有效的思维导图');
        return;
      }

      generatingMap.value = true;
      try {
        const response = await axios.post('/api/generate_mindmap', {
          content: content,
          title: noteTitle.value
        });

        if (response.data && response.data.success) {
          mindmapUrl.value = response.data.image_url;
          ElMessage.success('思维导图生成成功');
        } else {
          ElMessage.error('生成思维导图失败: ' + (response.data?.error || '未知错误'));
        }
      } catch (error) {
        console.error('生成思维导图出错:', error);
        ElMessage.error('生成思维导图失败，请重试');
      } finally {
        generatingMap.value = false;
      }
    };

    // 重新生成思维导图
    const regenerateMindmap = () => {
      ElMessageBox.confirm('确定要重新生成思维导图吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        generateMindmap();
      }).catch(() => { });
    };

    // 内容变化事件
    const change = (event) => {
      console.log('编辑器内容已更新');
    };

    // 页面加载时初始化
    onMounted(() => {
      // 如果有笔记ID，加载笔记数据
      loadNoteContent();
    });

    return {
      noteId,
      noteTitle,
      contentArea,
      addMenuVisible,
      quillEditor,
      loading,
      saving,
      mindmapUrl,
      generatingMap,
      goBack,
      undo,
      redo,
      finishNote,
      toggleAddMenu,
      insertImage,
      insertAudio,
      insertFile,
      change,
      generateMindmap,
      regenerateMindmap
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
  background-color: #f5f5f5;
  padding: 12px 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.title {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
}

.loading-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 15px;
  overflow-y: auto;
}

.title-input {
  margin-bottom: 15px;
}

.content-editor {
  flex: 1;
  min-height: 200px;
  margin-bottom: 15px;
}

.quillEditorChild {
  height: 100%;
  width: 100%;
}

.bottom-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background-color: #f5f5f5;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.toolbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.add-menu-content {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 15px;
}

.add-menu-item {
  width: 100px;
  height: 100px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.add-menu-item :deep(.el-card__header) {
  padding: 10px;
  text-align: center;
}

.text-container {
  text-align: center;
  font-size: 14px;
}

.mindmap-preview {
  margin-top: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  background-color: #f9f9f9;
}

.mindmap-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.mindmap-image {
  width: 100%;
  max-height: 300px;
}

.mindmap-error {
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

@media (max-width: 768px) {
  .header {
    padding: 8px 12px;
  }

  .editor-container {
    padding: 10px;
  }

  .bottom-toolbar {
    padding: 8px 12px;
  }

  .toolbar-right button {
    padding: 8px;
  }
}
</style>