<template>
  <keep-alive>
    <div class="editor-container">
      <div class="quillEditor"></div>
    </div>
  </keep-alive>
</template>

<script>
import { ref, onMounted, onActivated } from 'vue';
import Quill from 'quill';
import 'quill/dist/quill.snow.css';
import { ImageExtend, QuillWatch } from 'quill-image-extend-module';

// 注册图片扩展模块
Quill.register('modules/imageExtend', ImageExtend);

const titleConfig = {
  'ql-bold': '加粗',
  'ql-color': '颜色',
  'ql-font': '字体',
  'ql-code': '插入代码',
  'ql-italic': '斜体',
  'ql-link': '添加链接',
  'ql-background': '颜色',
  'ql-size': '字体大小',
  'ql-strike': '删除线',
  'ql-script': '上标/下标',
  'ql-underline': '下划线',
  'ql-blockquote': '引用',
  'ql-header': '标题',
  'ql-indent': '缩进',
  'ql-list': '列表',
  'ql-align': '文本对齐',
  'ql-direction': '文本方向',
  'ql-code-block': '代码块',
  'ql-formula': '公式',
  'ql-image': '图片',
  'ql-video': '视频',
  'ql-clean': '清除字体样式',
  'ql-upload': '文件',
  'ql-table': '插入表格',
  'ql-table-insert-row': '插入行',
  'ql-table-insert-column': '插入列',
  'ql-table-delete-row': '删除行',
  'ql-table-delete-column': '删除列'
};

export default {
  name: 'QuillEditor',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'contentData'],
  setup(props, { emit }) {
    const quill = ref(null);

    const options = {
      theme: 'snow',
      modules: {
        toolbar: {
          container: [
            ['bold', 'italic', 'underline', 'strike'],
            [{ header: 1 }, { header: 2 }],
            [{ list: 'ordered' }, { list: 'bullet' }],
            [{ indent: '-1' }, { indent: '+1' }],
            [{ color: [] }, { background: [] }],
            [{ font: [] }],
            [{ align: [] }],
            ['clean'],
            ['image'], // 添加图片按钮
            [
              { table: 'TD' },
              { 'table-insert-row': 'TIR' },
              { 'table-insert-column': 'TIC' },
              { 'table-delete-row': 'TDR' },
              { 'table-delete-column': 'TDC' }
            ]
          ],
          handlers: {
            table: function (val) {
              console.log(val);
              quill.value.getModule('table').insertTable(2, 3);
            },
            'table-insert-row': function () {
              quill.value.getModule('table').insertRowBelow();
            },
            'table-insert-column': function () {
              quill.value.getModule('table').insertColumnRight();
            },
            'table-delete-row': function () {
              quill.value.getModule('table').deleteRow();
            },
            'table-delete-column': function () {
              quill.value.getModule('table').deleteColumn();
            },
            image: function () {
              QuillWatch.emit(quill.value.id); // 触发图片上传
            }
          }
        },
        table: true,
        imageExtend: {
          loading: true, // 显示加载动画
          name: 'image', // 图片参数名
          action: 'https://localhost:5173', // 图片上传地址
          headers: (xhr) => {
            // 如果需要，可以在这里添加请求头
          },
          response: (res) => {
            return res.url; // 返回图片的URL
          }
        }
      },
      placeholder: ''
    };

    const addQuillTitle = () => {
      const oToolBar = document.querySelector('.ql-toolbar');
      const aButton = oToolBar.querySelectorAll('button');
      const aSelect = oToolBar.querySelectorAll('select');
      aButton.forEach(function (item) {
        if (item.className === 'ql-script') {
          item.value === 'sub' ? (item.title = '下标') : (item.title = '上标');
        } else if (item.className === 'ql-indent') {
          item.value === '+1' ? (item.title = '向右缩进') : (item.title = '向左缩进');
        } else {
          item.title = titleConfig[item.classList[0]];
        }
      });
      aSelect.forEach(function (item) {
        item.parentNode.title = titleConfig[item.classList[0]];
      });
    };

    const getContentData = () => {
      return quill.value.getContents();
    };

    const getQuillInstance = () => {
      return quill.value;
    };

    onMounted(() => {
      const dom = document.querySelector('.quillEditor');
      quill.value = new Quill(dom, options);
      quill.value.on('text-change', () => {
        emit('contentData', quill.value.root.innerHTML);
      });

      // 设置表格按钮的图标
      document.querySelector('.ql-table-insert-row').innerHTML = `<svg t="1591862376726" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6306" width="18" height="200"><path d="M500.8 604.779L267.307 371.392l-45.227 45.27 278.741 278.613L779.307 416.66l-45.248-45.248z" p-id="6307"></path></svg>`;
      document.querySelector('.ql-table-insert-column').innerHTML = `<svg t="1591862238963" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6509" width="18" height="200"><path d="M593.450667 512.128L360.064 278.613333l45.290667-45.226666 278.613333 278.762666L405.333333 790.613333l-45.226666-45.269333z" p-id="6510"></path></svg>`;
      document.querySelector('.ql-table-delete-row').innerHTML = `<svg t="1591862253524" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6632" width="18" height="200"><path d="M500.8 461.909333L267.306667 695.296l-45.226667-45.269333 278.741333-278.613334L779.306667 650.026667l-45.248 45.226666z" p-id="6633"></path></svg>`;
      document.querySelector('.ql-table-delete-column').innerHTML = `<svg t="1591862261059" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6755" width="18" height="200"><path d="M641.28 278.613333l-45.226667-45.226666-278.634666 278.762666 278.613333 278.485334 45.248-45.269334-233.365333-233.237333z" p-id="6756"></path></svg>`;
      addQuillTitle();
    });

    onActivated(() => {
      quill.value.setContents({});
    });

    return {
      quill,
      getContentData,
      getQuillInstance
    };
  }
};
</script>

<style scoped>
.quillEditor {
  width: auto; /* 允许宽度根据内容自适应 */
  display: inline-block; /* 让宽度根据内容自适应 */
}

.quillEditor .ql-editor {
  width: 100%; /* 确保编辑器内容区域宽度为 100% */
}

.quillEditor .ql-editor table {
  width: 100%; /* 确保表格宽度自适应容器宽度 */
}

.quillEditor .ql-editor table {
  width: max-content; /* 根据表格内容的宽度来调整宽度 */
}

/* 模态框背景 */
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* 放大图片样式 */
.large-image {
  max-width: 90%;
  max-height: 90%;
}

/* 关闭按钮样式 */
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  color: white;
  cursor: pointer;
}
</style>