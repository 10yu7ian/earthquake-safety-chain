<template>
  <div class="resident-page">
    <div class="ambient" aria-hidden="true">
      <div class="ring" />
      <div class="grid" />
    </div>

    <header class="top-nav">
      <div class="brand">
        <div class="logo-box">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
            <path
              d="M12 2L4.5 5v6.5c0 4.7 3.2 9 7.5 10.5 4.3-1.5 7.5-5.8 7.5-10.5V5L12 2z"
              stroke="url(#ng)"
              stroke-width="1.8"
            />
            <defs>
              <linearGradient id="ng" x1="0" y1="0" x2="24" y2="24">
                <stop offset="0%" stop-color="#00d1ff" />
                <stop offset="100%" stop-color="#a855f7" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="brand-name">
          <span class="gradient-text">地震安链</span>
          <small>我的设备</small>
        </div>
      </div>

      <div class="nav-right">
        <div v-if="showDemoSwitch" class="demo-switch">
          <span>演示状态</span>
          <el-switch
            :model-value="deviceStatus === 'cutoff'"
            inline-prompt
            active-text="切断"
            inactive-text="正常"
            @change="toggleStatus"
          />
        </div>
        <el-button plain @click="handleLogout">退出</el-button>
      </div>
    </header>

    <main class="content">
      <section class="status-hero glass-panel" :class="{ alert: isCutoff }">
        <div class="hero-left">
          <div class="status-kicker">{{ isCutoff ? "紧急通知" : "系统状态" }}</div>
          <h1 class="status-big">
            {{ isCutoff ? "已紧急切断" : "安全在线" }}
          </h1>
          <p class="status-sub">
            {{ isCutoff
              ? "请撤离至开阔地带，等待专业人员处置"
              : "全天候实时监测，您所在的社区一切正常"
            }}
          </p>

          <div class="hero-meta">
            <div class="meta-chip">
              <span class="dot" :class="isCutoff ? 'red' : 'green'" />
              <span>{{ isCutoff ? "燃气已切断" : "设备守护中" }}</span>
            </div>
            <div class="meta-chip">
              <span class="text-mono time">{{ currentTime }}</span>
            </div>
          </div>
        </div>

        <div class="hero-right">
          <div class="shield" :class="{ alert: isCutoff }">
            <div class="ring r1" />
            <div class="ring r2" />
            <div class="ring r3" />
            <svg class="shield-svg" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M12 2L4.5 5v6.5c0 4.7 3.2 9 7.5 10.5 4.3-1.5 7.5-5.8 7.5-10.5V5L12 2z"
                stroke="currentColor"
                stroke-width="1.6"
              />
              <path
                v-if="!isCutoff"
                d="M9 12l2.2 2.2L15.2 10.2"
                stroke="currentColor"
                stroke-width="1.6"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                v-else
                d="M9 9l6 6M15 9l-6 6"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
              />
            </svg>
          </div>
        </div>
      </section>

      <section v-if="isCutoff" class="danger-block">
        <div class="danger-title">
          <span class="flash" />
          紧急处置指引
        </div>
        <p>
          请立即关闭燃气总阀，打开窗户通风，并撤离至安全地带。等待燃气公司检修，或在确认安全后点击「自检」进行远程恢复。
        </p>
      </section>

      <section class="info-grid">
        <div class="info-card glass-panel">
          <div class="ic-head">
            <span class="kicker">我的设备</span>
            <h3>{{ deviceInfo.name }}</h3>
          </div>
          <div class="ic-rows">
            <div class="row">
              <span>设备编号</span>
              <strong class="text-mono neon">{{ deviceInfo.id }}</strong>
            </div>
            <div class="row">
              <span>安装位置</span>
              <strong>{{ deviceInfo.location }}</strong>
            </div>
            <div class="row">
              <span>上次触发</span>
              <strong class="text-mono">{{ deviceInfo.lastTriggerTime }}</strong>
            </div>
            <div class="row">
              <span>电池电量</span>
              <div class="battery">
                <span class="battery-bar">
                  <i :style="{ width: deviceInfo.battery + '%' }" />
                </span>
                <strong>{{ deviceInfo.battery }}%</strong>
              </div>
            </div>
          </div>
        </div>

        <div class="count-card glass-panel">
          <div class="kicker">累计拦截</div>
          <div class="count-num">{{ deviceInfo.totalIntercepts }}</div>
          <div class="count-sub">为您阻止 {{ deviceInfo.totalIntercepts }} 次潜在事故</div>
          <div class="count-glow" />
        </div>
      </section>

      <section class="action-row">
        <el-button
          class="check-btn"
          type="primary"
          :disabled="isCutoff && false"
          @click="handleSelfCheck"
        >
          <span class="btn-icon">⟳</span>
          立即自检
        </el-button>
        <el-button class="secondary-btn" plain>
          <span class="btn-icon">☏</span>
          一键报警
        </el-button>
      </section>

      <footer class="foot">
        <span>遇误切断？联系物业：<strong>400-xxx-xxxx</strong></span>
        <span class="sep">·</span>
        <span>地震安链 · v1.0.0 (2026)</span>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElLoading, ElMessage } from "element-plus";
import { getDevices, getEvents, getStatistics, sendControl } from "@/api";

const showDemoSwitch =
  import.meta.env.VITE_DEMO_MODE === "true" ||
  (import.meta.env.DEV && import.meta.env.VITE_ENABLE_RESIDENT_DEMO_SWITCH !== "false");
const router = useRouter();

const deviceStatus = ref("normal");
const isCutoff = computed(() => deviceStatus.value === "cutoff");
const deviceInfo = ref({
  id: "--",
  name: "暂无设备",
  location: "--",
  lastTriggerTime: "--",
  totalIntercepts: 0,
  battery: 0,
});

const currentTime = ref("");
let timer = null;

const formatTime = () => {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  currentTime.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

const toggleStatus = (value) => {
  deviceStatus.value = value ? "cutoff" : "normal";
};

const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  router.push("/login");
};

const handleSelfCheck = () => {
  const loading = ElLoading.service({
    lock: true,
    text: "正在检测硬件状态...",
    background: "rgba(4, 6, 12, 0.7)",
  });
  window.setTimeout(async () => {
    try {
      if (deviceInfo.value.id && deviceInfo.value.id !== "--") {
        await sendControl(deviceInfo.value.id, "self_check");
      }
    } catch (error) {
      ElMessage.error(error?.response?.data?.detail || "下发自检指令失败");
      loading.close();
      return;
    }
    loading.close();
    ElMessage.success("自检完成，设备正常，待管理员远程复位");
  }, 2500);
};

const loadResidentData = async () => {
  try {
    const [devicesData, eventsData, statsData] = await Promise.all([
      getDevices({ limit: 200 }),
      getEvents({ limit: 200 }),
      getStatistics(),
    ]);
    const devices = Array.isArray(devicesData) ? devicesData : [];
    const events = Array.isArray(eventsData) ? eventsData : [];
    const target = devices[0];
    if (!target) return;

    const ownEvents = events.filter((e) => e.device_id === target.id);
    const lastEvent = ownEvents[0];
    const totalIntercepts = ownEvents.filter((e) => e.event_type === "切断").length;

    deviceInfo.value = {
      id: target.id,
      name: target.name || target.id,
      location: target.location || "--",
      lastTriggerTime: lastEvent?.created_at ? String(lastEvent.created_at).replace("T", " ").slice(0, 19) : "--",
      totalIntercepts: statsData?.today_triggers ?? totalIntercepts,
      battery: 86,
    };
    deviceStatus.value = target.status === "cutoff" ? "cutoff" : "normal";
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "加载居民看板数据失败");
  }
};

onMounted(() => {
  formatTime();
  timer = window.setInterval(formatTime, 1000);
  loadResidentData();
});

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<style scoped lang="scss">
.resident-page {
  position: relative;
  min-height: 100vh;
  padding: 20px 28px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.ambient {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: -1;
}

.ambient .ring {
  position: absolute;
  top: -220px;
  left: 50%;
  transform: translateX(-50%);
  width: 880px;
  height: 880px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 209, 255, 0.18), transparent 60%);
  filter: blur(60px);
}

.ambient .grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at 50% 30%, #000 20%, transparent 70%);
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  border-radius: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-box {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: rgba(0, 209, 255, 0.1);
  border: 1px solid rgba(0, 209, 255, 0.4);
  box-shadow: 0 0 18px rgba(0, 209, 255, 0.25);
}

.brand-name {
  display: flex;
  flex-direction: column;
  line-height: 1.15;

  .gradient-text {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.04em;
  }

  small {
    color: #64748b;
    font-size: 11px;
    letter-spacing: 0.24em;
    margin-top: 3px;
  }
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.demo-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #a8b0bd;
  font-size: 12px;
}

.content {
  max-width: 1080px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.kicker {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(0, 209, 255, 0.08);
  border: 1px solid rgba(0, 209, 255, 0.3);
  color: #a8eaff;
  font-size: 11px;
  letter-spacing: 0.18em;
}

.status-hero {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: center;
  padding: 40px 40px;
  border-radius: 24px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.status-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(
    420px 200px at 0% 0%,
    rgba(34, 211, 165, 0.18),
    transparent 65%
  );
  pointer-events: none;
}

.status-hero.alert {
  border-color: rgba(255, 84, 112, 0.55) !important;
  box-shadow: 0 0 0 1px rgba(255, 84, 112, 0.35), 0 0 48px rgba(255, 84, 112, 0.18);
}

.status-hero.alert::before {
  background: radial-gradient(
    420px 200px at 0% 0%,
    rgba(255, 84, 112, 0.25),
    transparent 65%
  );
  animation: alert-pulse-bg 1.6s infinite;
}

.status-kicker {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 999px;
  background: rgba(34, 211, 165, 0.12);
  border: 1px solid rgba(34, 211, 165, 0.45);
  color: #7ff3d1;
  font-size: 12px;
  letter-spacing: 0.18em;
}

.status-hero.alert .status-kicker {
  background: rgba(255, 84, 112, 0.12);
  border-color: rgba(255, 84, 112, 0.55);
  color: #ffb3c1;
}

.status-big {
  margin: 18px 0 10px;
  font-size: 64px;
  line-height: 1;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: #22d3a5;
  text-shadow: 0 0 24px rgba(34, 211, 165, 0.55), 0 0 48px rgba(34, 211, 165, 0.25);
}

.status-hero.alert .status-big {
  color: #ff5470;
  text-shadow: 0 0 24px rgba(255, 84, 112, 0.65), 0 0 48px rgba(255, 84, 112, 0.3);
}

.status-sub {
  margin: 0;
  color: #cbd5e1;
  font-size: 15px;
  max-width: 460px;
}

.hero-meta {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  font-size: 13px;
}

.meta-chip .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.meta-chip .dot.green {
  background: #22d3a5;
  box-shadow: 0 0 10px rgba(34, 211, 165, 0.8);
}

.meta-chip .dot.red {
  background: #ff5470;
  box-shadow: 0 0 10px rgba(255, 84, 112, 0.85);
  animation: pulse-dot 1.2s infinite;
}

.meta-chip .time {
  color: #00d1ff;
  letter-spacing: 0.05em;
  text-shadow: 0 0 8px rgba(0, 209, 255, 0.45);
}

.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}

.shield {
  position: relative;
  width: 220px;
  height: 220px;
  display: grid;
  place-items: center;
  color: #22d3a5;
}

.shield.alert {
  color: #ff5470;
  animation: alert-blink 1.1s infinite;
}

.shield .ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid currentColor;
  opacity: 0.35;
}

.shield .r1 { inset: 0; }
.shield .r2 { inset: 18px; opacity: 0.22; }
.shield .r3 { inset: 36px; opacity: 0.14; }

.shield-svg {
  width: 118px;
  height: 118px;
  filter: drop-shadow(0 0 20px currentColor);
}

.danger-block {
  padding: 16px 20px;
  border-radius: 16px;
  background: rgba(255, 84, 112, 0.1);
  border: 1px solid rgba(255, 84, 112, 0.5);
  color: #fecaca;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 24px rgba(255, 84, 112, 0.2);
}

.danger-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #ff5470;
  font-size: 15px;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.danger-title .flash {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff5470;
  box-shadow: 0 0 12px rgba(255, 84, 112, 0.9);
  animation: pulse-dot 1s infinite;
}

.danger-block p {
  margin: 0;
  line-height: 1.7;
  color: #ffb3c1;
  font-size: 14px;
}

.info-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.info-card,
.count-card {
  padding: 22px 24px;
  border-radius: 18px;
}

.ic-head {
  margin-bottom: 14px;

  h3 {
    margin: 8px 0 0;
    color: #f1f5f9;
    font-size: 20px;
    font-weight: 700;
  }
}

.ic-rows {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  font-size: 14px;
}

.row:last-child {
  border-bottom: none;
}

.row span {
  color: #94a3b8;
}

.row strong {
  color: #f1f5f9;
  font-weight: 500;
}

.row strong.neon {
  color: #00d1ff;
  text-shadow: 0 0 10px rgba(0, 209, 255, 0.4);
}

.battery {
  display: flex;
  align-items: center;
  gap: 10px;
}

.battery-bar {
  width: 90px;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
  display: inline-block;
}

.battery-bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #22d3a5, #38e7ff);
  box-shadow: 0 0 12px rgba(34, 211, 165, 0.5);
}

.count-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  gap: 10px;
  overflow: hidden;
}

.count-num {
  font-size: 72px;
  font-weight: 900;
  line-height: 1;
  font-family: var(--font-family-mono);
  color: #a855f7;
  text-shadow: 0 0 28px rgba(168, 85, 247, 0.6), 0 0 48px rgba(168, 85, 247, 0.3);
  letter-spacing: 0.02em;
}

.count-sub {
  color: #94a3b8;
  font-size: 13px;
}

.count-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(200px 140px at 100% 100%, rgba(168, 85, 247, 0.25), transparent 70%);
}

.action-row {
  display: flex;
  gap: 14px;
}

.check-btn {
  flex: 1;
  height: 60px;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.32em;
  border-radius: 14px;
}

.secondary-btn {
  flex: 0 0 180px;
  height: 60px;
  font-size: 15px;
  letter-spacing: 0.18em;
  border-radius: 14px;
}

.btn-icon {
  margin-right: 8px;
  font-family: var(--font-family-mono);
  font-size: 18px;
}

.foot {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.04em;
  padding-top: 6px;
  flex-wrap: wrap;
}

.foot strong {
  color: #00d1ff;
  text-shadow: 0 0 8px rgba(0, 209, 255, 0.4);
  font-family: var(--font-family-mono);
}

.foot .sep { color: #334155; }

@keyframes alert-blink {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.04); opacity: 0.75; }
}

@keyframes alert-pulse-bg {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.4); opacity: 0.6; }
}

@media (max-width: 900px) {
  .status-hero {
    grid-template-columns: 1fr;
    padding: 28px 24px;
  }
  .hero-right {
    order: -1;
  }
  .status-big {
    font-size: 46px;
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
  .action-row {
    flex-direction: column;
  }
  .secondary-btn {
    flex: 1;
  }
}
</style>
