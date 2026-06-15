import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    // 用 127.0.0.1 避免 Windows 上 localhost 解析到 ::1，而后端只监听 127.0.0.1 导致代理连不上、登录失败
    host: true,
    port: 5173,
    strictPort: false,
    open: "/login",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
