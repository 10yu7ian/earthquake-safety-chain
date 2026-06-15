import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import * as echarts from "echarts";
import "./styles/theme.scss";
import "./styles/element-override.scss";

const app = createApp(App);

Object.entries(ElementPlusIconsVue).forEach(([key, component]) => {
  app.component(key, component);
});

app.config.globalProperties.$echarts = echarts;

app.use(router);
app.use(ElementPlus);
app.mount("#app");
