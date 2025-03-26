<template>
    <div class="common-layout">
      <el-container>
        <el-header class="common-header flex-float">
          <div class="flex">
            <img class="logo" src="../assets/feidudu.jpg" alt="">
            <h1 class="title">智能笔记助手系统</h1>
          </div>
          <el-button type="danger" @click="loginOut">退出</el-button>
   
        </el-header>
        <el-container>
          <el-aside class="common-aside" width="200px">
            <el-menu background-color="none" text-color="#fff" :router="true">
              <el-sub-menu index="1">
                <template #title>
                  <el-icon>
                    <location />
                  </el-icon>
                  <span>历史笔记</span>
                </template>
                <el-menu-item-group>
                  <el-menu-item index="/note">笔记列表</el-menu-item>
                </el-menu-item-group>
              </el-sub-menu>
              <el-sub-menu index="2">
                <template #title>
                  <el-icon>
                    <location />
                  </el-icon>
                  <span>新增笔记</span>
                </template>
                <el-menu-item-group>
                  <el-menu-item index="/noteAdd">新增笔记1</el-menu-item>
                </el-menu-item-group>
                <el-menu-item-group>
                  <el-menu-item index="/noteAdd2">新增笔记2</el-menu-item>
                </el-menu-item-group>
              </el-sub-menu>
   
            </el-menu>
   
          </el-aside>
          <el-main>
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </template>
  <script>
  import { useStore } from 'vuex'
  import { useRouter } from 'vue-router'
  export default {
    name: "layout",
    setup() {
      const store = useStore()
      const router = useRouter()
      const loginOut = () => {
        //localStorage.removeItem("loginData")删除对应的登录信息
        //store.commit("setUserInfo", {})
        router.push(
          {
            path: './login'
          })
      }
      return {
        loginOut
   
      }
    }
   
  }
  </script>
  <style>
  .el-container {
    height: 100vh;
  }
   
  .common-header {
    background: rgb(47, 44, 54);
    display: flex;
  }
   
  .common-aside {
    background: rgb(88, 85, 96);
  }
   
  .logo {
    width: 80px;
  }
   
  .title {
    color: #fff;
  }
  .el-main{
    background: #efefef;
   
  }
  </style>
  