import { createRouter, createWebHistory } from 'vue-router';
import Note from '../components/Note.vue';
import NoteAdd from '../components/NoteAdd.vue';
import NoteAdd2 from '../components/NoteAdd2.vue';
import Login from '../components/Login.vue';
import Layout from '../components/Layout.vue';
const routes = [
  {
    path: '/layout',
    name: 'Layout',
    component: Layout,
    children:[
       {
          path: '/note',
          name: 'Note',
          component: Note,
        },
        {
          path: '/noteAdd',
          name: 'NoteAdd',
          component: NoteAdd,
        },
        {
          path: '/noteAdd2',
          name: 'NoteAdd2',
          component: NoteAdd2,
        },
    ]
  },
  {
      path:'/',
      name : 'Login',
      component: Login,
  },
];

const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 历史模式
  routes, // 路由配置
});

export default router;