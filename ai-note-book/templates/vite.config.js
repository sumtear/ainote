import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";

export default defineConfig({
  plugins: [
    vue(), // Vue 插件
    AutoImport({
      resolvers: [ElementPlusResolver()], // 自动导入 Element Plus 的 API
    }),
    Components({
      resolvers: [ElementPlusResolver()], // 自动导入 Element Plus 的组件
    }),
  ],
  // 添加服务器代理配置
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
        secure: false,
      },
      "/generate-mindmap": {
        target: "http://localhost:5000",
        changeOrigin: true,
        secure: false,
      },
      "/mindmap-images": {
        target: "http://localhost:5000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
