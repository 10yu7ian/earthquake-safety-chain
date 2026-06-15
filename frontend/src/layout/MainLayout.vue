<template>
  <div class="main-layout">
    <aside class="sidebar glass-panel">
      <div class="logo-area">
        <div class="logo-mark">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true">
            <path
              d="M12 2L4.5 5v6.5c0 4.7 3.2 9 7.5 10.5 4.3-1.5 7.5-5.8 7.5-10.5V5L12 2z"
              stroke="url(#lg)"
              stroke-width="1.8"
            />
            <path
              d="M9 12l2.2 2.2L15.2 10.2"
              stroke="url(#lg)"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <defs>
              <linearGradient id="lg" x1="0" y1="0" x2="24" y2="24">
                <stop offset="0%" stop-color="#00d1ff" />
                <stop offset="100%" stop-color="#a855f7" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="logo-text">
          <span class="brand gradient-text">地震安链</span>
          <span class="brand-sub">地震安链 · 安全联防</span>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        :router="true"
        class="sidebar-menu"
        mode="vertical"
        background-color="transparent"
        text-color="#cbd5e1"
        active-text-color="#00d1ff"
      >
        <el-menu-item index="/dashboard">
          <span class="nav-dot" />
          <span>驾驶舱</span>
        </el-menu-item>
        <el-menu-item index="/devices">
          <span class="nav-dot" />
          <span>设备管理</span>
        </el-menu-item>
        <el-menu-item index="/events">
          <span class="nav-dot" />
          <span>事件记录</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <span class="nav-dot" />
          <span>数据报表</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="status-row">
          <span class="status-dot online" />
          <span>服务在线</span>
        </div>
        <span class="version">v1.0.0 · 2026</span>
      </div>
    </aside>

    <section class="main-section">
      <header class="topbar glass-panel">
        <div class="title-wrap">
          <span class="title-bar" />
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="topbar-actions">
          <div class="env-chip">
            <span class="pulse" />
            实时监控中
          </div>
          <div class="avatar-placeholder" aria-label="管理员头像">管</div>
          <el-button plain @click="handleLogout">退出</el-button>
        </div>
      </header>

      <main class="content-area">
        <router-view />
        <slot />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

defineProps({
  pageTitle: {
    type: String,
    default: "驾驶舱",
  },
});

const router = useRouter();
const route = useRoute();

const activeMenu = computed(() => {
  if (route.path.startsWith("/dashboard")) return "/dashboard";
  if (route.path.startsWith("/devices")) return "/devices";
  if (route.path.startsWith("/events")) return "/events";
  if (route.path.startsWith("/reports")) return "/reports";
  return route.path;
});

const handleLogout = () => {
  localStorage.clear();
  router.push("/login");
};
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  min-height: 100vh;
  padding: 14px;
  gap: 14px;
}

.sidebar {
  width: 248px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-radius: 22px;
  padding: 18px 14px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.045) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 10px 40px rgba(0, 0, 0, 0.45);
  position: relative;
  overflow: hidden;

  &::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(
      400px 140px at 0% 0%,
      rgba(0, 209, 255, 0.16),
      transparent 60%
    );
    pointer-events: none;
  }
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 8px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 12px;
}

.logo-mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(0, 209, 255, 0.1);
  border: 1px solid rgba(0, 209, 255, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 18px rgba(0, 209, 255, 0.25);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.brand-sub {
  font-size: 10px;
  color: #64748b;
  letter-spacing: 0.22em;
  margin-top: 2px;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  flex: 1;
  padding: 4px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 4px 0;
  border-radius: 10px;
  padding: 0 14px !important;
  color: #a8b0bd;
  font-weight: 500;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  transition: background 0.2s ease, color 0.2s ease;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(
    90deg,
    rgba(0, 209, 255, 0.18) 0%,
    rgba(168, 85, 247, 0.1) 100%
  );
  color: #00d1ff !important;
  box-shadow: inset 0 0 0 1px rgba(0, 209, 255, 0.3),
    0 0 18px rgba(0, 209, 255, 0.18);
  text-shadow: 0 0 14px rgba(0, 209, 255, 0.5);
}

.sidebar-menu :deep(.el-menu-item.is-active)::before {
  content: "";
  position: absolute;
  left: -2px;
  top: 10px;
  bottom: 10px;
  width: 3px;
  border-radius: 3px;
  background: linear-gradient(180deg, #00d1ff 0%, #a855f7 100%);
  box-shadow: 0 0 12px rgba(0, 209, 255, 0.6);
}

.nav-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}

.sidebar-menu :deep(.el-menu-item:hover) .nav-dot {
  background: rgba(0, 209, 255, 0.6);
}

.sidebar-menu :deep(.el-menu-item.is-active) .nav-dot {
  background: #00d1ff;
  box-shadow: 0 0 10px rgba(0, 209, 255, 0.8);
}

.sidebar-footer {
  margin-top: auto;
  padding: 14px 12px 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22d3a5;
  box-shadow: 0 0 10px rgba(34, 211, 165, 0.8);
  animation: pulse-soft 2s infinite;
}

.version {
  font-family: var(--font-family-mono);
  color: #475569;
}

.main-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.topbar {
  height: 64px;
  flex-shrink: 0;
  border-radius: 16px;
  padding: 0 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-bar {
  width: 4px;
  height: 22px;
  border-radius: 4px;
  background: linear-gradient(180deg, #00d1ff, #a855f7);
  box-shadow: 0 0 12px rgba(0, 209, 255, 0.55);
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: 0.04em;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.env-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(34, 211, 165, 0.4);
  background: rgba(34, 211, 165, 0.08);
  color: #7ff3d1;
  font-size: 12px;
  letter-spacing: 0.04em;
}

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22d3a5;
  box-shadow: 0 0 10px rgba(34, 211, 165, 0.8);
  animation: pulse-soft 1.6s infinite;
}

.avatar-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 209, 255, 0.25), rgba(168, 85, 247, 0.25));
  border: 1px solid rgba(0, 209, 255, 0.4);
  color: #e2e8f0;
  font-weight: 600;
  box-shadow: 0 0 14px rgba(0, 209, 255, 0.25);
}

.content-area {
  flex-grow: 1;
  padding: 6px 4px 10px;
  overflow-y: auto;
}

@keyframes pulse-soft {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.65;
  }
}
</style>
