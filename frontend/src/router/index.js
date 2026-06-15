import { createRouter, createWebHistory } from "vue-router";

// 页面组件采用懒加载，后续可根据业务需要补充静态导入或分组策略
// import Login from "@/views/Login.vue";
// import Dashboard from "@/views/Dashboard.vue";
// import Devices from "@/views/Devices.vue";
// import Events from "@/views/Events.vue";
// import Reports from "@/views/Reports.vue";
// import ResidentDashboard from "@/views/ResidentDashboard.vue";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/Dashboard.vue"),
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/devices",
    name: "Devices",
    component: () => import("@/views/Devices.vue"),
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/events",
    name: "Events",
    component: () => import("@/views/Events.vue"),
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/reports",
    name: "Reports",
    component: () => import("@/views/Reports.vue"),
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/resident",
    name: "ResidentDashboard",
    component: () => import("@/views/ResidentDashboard.vue"),
    meta: { requiresAuth: true, role: "resident" },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (to.meta.requiresAuth && !token) {
    return "/login";
  }

  if (token && to.path === "/login") {
    if (role === "admin") {
      return "/dashboard";
    }
    if (role === "resident") {
      return "/resident";
    }
  }

  if (token && to.meta.requiresAuth) {
    const targetRole = to.meta.role;

    if (targetRole && role !== targetRole) {
      if (role === "admin" && targetRole === "resident") {
        return "/dashboard";
      }
      if (role === "resident" && targetRole === "admin") {
        return "/resident";
      }
      return "/login";
    }
  }

  return true;
});

export default router;
