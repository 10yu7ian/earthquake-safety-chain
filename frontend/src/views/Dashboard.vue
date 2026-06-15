<template>
  <MainLayout page-title="驾驶舱">
    <div class="dashboard-page">
      <section class="kpi-row">
        <div
          v-for="item in kpiList"
          :key="item.key"
          class="kpi-card glass-panel"
          :class="['tone-' + item.tone]"
        >
          <div class="kpi-meta">
            <span class="kpi-label">{{ item.label }}</span>
            <span class="kpi-trend" :class="item.up ? 'up' : 'down'">
              {{ item.up ? "▲" : "▼" }} {{ item.trend }}
            </span>
          </div>
          <div class="kpi-value-line">
            <span class="kpi-value">{{ item.value }}</span>
            <span class="kpi-unit">{{ item.unit }}</span>
          </div>
          <div class="kpi-spark">
            <span
              v-for="(h, i) in item.spark"
              :key="i"
              class="bar"
              :style="{ height: h + '%' }"
            />
          </div>
          <div class="kpi-glow" />
        </div>
      </section>

      <section class="middle-row">
        <div class="map-card glass-panel">
          <div class="panel-head">
            <div>
              <span class="kicker">实时节点</span>
              <h3>设备分布地图</h3>
            </div>
            <div class="legend">
              <span class="legend-item"><i class="dot dot-green" />正常 {{ stats.normal }}</span>
              <span class="legend-item"><i class="dot dot-orange" />异常 {{ stats.warn }}</span>
              <span class="legend-item"><i class="dot dot-red" />告警 {{ stats.alert }}</span>
            </div>
          </div>
          <div ref="mapContainer" class="map-container" />
          <div class="map-overlay-tr">
            <div class="overlay-row">
              <span class="label">覆盖社区</span>
              <span class="value">{{ stats.community }}</span>
            </div>
            <div class="overlay-row">
              <span class="label">今日在线率</span>
              <span class="value neon-cyan">{{ stats.onlineRate }}%</span>
            </div>
          </div>
        </div>

        <div class="events-card glass-panel">
          <div class="panel-head">
            <div>
              <span class="kicker">最近事件</span>
              <h3>实时事件流</h3>
            </div>
            <span class="live">
              <i class="pulse" /> LIVE
            </span>
          </div>
          <ul class="event-stream">
            <li
              v-for="ev in recentEvents"
              :key="ev.time + ev.deviceId"
              :class="['event-item', ev.type === '切断' ? 'danger' : '']"
            >
              <div class="time">{{ ev.time.slice(11) }}</div>
              <div class="content">
                <div class="row-1">
                  <span class="device-id text-mono">{{ ev.deviceId }}</span>
                  <el-tag
                    :type="ev.type === '切断' ? 'danger' : ev.type === '恢复' ? 'success' : 'info'"
                    size="small"
                  >
                    {{ ev.type }}
                  </el-tag>
                </div>
                <div class="row-2">
                  <span>PGA {{ ev.peakAcceleration }}</span>
                  <span class="sep">·</span>
                  <span>{{ ev.location }}</span>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </section>

      <section class="bottom-row">
        <div class="activity-card glass-panel">
          <div class="panel-head">
            <div>
              <span class="kicker">24 小时</span>
              <h3>活跃度热力</h3>
            </div>
            <span class="legend-item"><i class="dot dot-cyan" />每小时事件数</span>
          </div>
          <div class="heatmap">
            <span
              v-for="(v, i) in hourly"
              :key="i"
              class="cell"
              :style="{ '--h': v }"
            >
              <em>{{ i }}</em>
            </span>
          </div>
        </div>

        <div class="summary-card glass-panel">
          <div class="panel-head">
            <div>
              <span class="kicker">系统指标</span>
              <h3>核心健康度</h3>
            </div>
          </div>
          <div class="metric-list">
            <div class="metric" v-for="m in systemMetrics" :key="m.label">
              <div class="m-head">
                <span>{{ m.label }}</span>
                <span class="m-value" :style="{ color: m.color }">{{ m.value }}{{ m.unit }}</span>
              </div>
              <div class="m-bar">
                <span
                  :style="{ width: m.percent + '%', background: m.gradient }"
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="deviceDialogVisible" width="460px" title="设备详情">
      <div v-if="selectedDevice" class="device-detail">
        <p><span>设备ID</span><strong class="text-mono">{{ selectedDevice.deviceId }}</strong></p>
        <p><span>设备名称</span><strong>{{ selectedDevice.name }}</strong></p>
        <p>
          <span>状态</span>
          <el-tag :type="selectedDevice.status === 'alert' ? 'danger' : 'success'" size="small">
            {{ selectedDevice.statusText }}
          </el-tag>
        </p>
        <p><span>位置</span><strong>{{ selectedDevice.position }}</strong></p>
        <p><span>最近心跳</span><strong>{{ selectedDevice.lastHeartbeat }}</strong></p>
      </div>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleRemoteReset">远程复位</el-button>
      </template>
    </el-dialog>
  </MainLayout>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import MainLayout from "@/layout/MainLayout.vue";
import { getDevices, getEvents, getStatistics, sendControl } from "@/api";

const mapContainer = ref(null);
const leafletMap = ref(null);
const deviceDialogVisible = ref(false);
const selectedDevice = ref(null);

const devices = ref([]);
const events = ref([]);
const statistics = ref(null);

const recentEvents = computed(() =>
  events.value.slice(0, 6).map((ev) => ({
    time: ev.created_at ? String(ev.created_at).replace("T", " ").slice(0, 19) : "--",
    deviceId: ev.device_id,
    type: ev.event_type || "未知",
    peakAcceleration: ev.acc_max === null || ev.acc_max === undefined ? "--" : `${ev.acc_max}g`,
    location: devices.value.find((d) => d.id === ev.device_id)?.location || "--",
  }))
);

const stats = computed(() => {
  const total = statistics.value?.total_devices ?? devices.value.length;
  const online = statistics.value?.online_devices ?? devices.value.filter((d) => d.status === "online").length;
  const alert =
    statistics.value?.alert_count ??
    devices.value.filter((d) => d.status === "triggered" || d.status === "cutoff").length;
  const warn = devices.value.filter((d) => d.status === "offline").length;
  const communityCount = new Set(devices.value.map((d) => d.community).filter(Boolean)).size;
  const onlineRate = total ? Number(((online / total) * 100).toFixed(1)) : 0;
  return {
    normal: online,
    warn,
    alert,
    community: communityCount,
    onlineRate,
  };
});

const kpiList = computed(() => [
  { key: "totalDevices", label: "总设备数", value: String(statistics.value?.total_devices ?? devices.value.length), unit: "台", tone: "cyan", trend: "实时", up: true, spark: [34, 48, 56, 62, 70, 78, 88] },
  { key: "onlineDevices", label: "在线设备", value: String(statistics.value?.online_devices ?? stats.value.normal), unit: "台", tone: "violet", trend: `${stats.value.onlineRate}%`, up: true, spark: [40, 52, 58, 63, 74, 79, 86] },
  { key: "todayEvents", label: "今日事件", value: String(statistics.value?.today_events ?? events.value.length), unit: "条", tone: "warn", trend: "实时", up: true, spark: [28, 36, 44, 49, 54, 61, 68] },
  { key: "intercepts", label: "今日拦截", value: String(statistics.value?.today_triggers ?? 0), unit: "次", tone: "danger", trend: "实时", up: false, spark: [64, 60, 58, 48, 42, 35, 30] },
]);

const hourly = computed(() => {
  const arr = Array(24).fill(0.08);
  events.value.forEach((ev) => {
    if (!ev.created_at) return;
    const h = new Date(ev.created_at).getHours();
    if (Number.isInteger(h) && h >= 0 && h < 24) arr[h] += 0.12;
  });
  const max = Math.max(...arr, 0.1);
  return arr.map((v) => Math.min(1, v / max));
});

const systemMetrics = computed(() => {
  const total = statistics.value?.total_devices ?? devices.value.length;
  const online = statistics.value?.online_devices ?? stats.value.normal;
  const availability = total ? Number(((online / total) * 100).toFixed(2)) : 0;
  return [
    { label: "服务可用性", value: availability.toFixed(2), unit: "%", percent: Math.min(100, availability), color: "#00d1ff", gradient: "linear-gradient(90deg, #00d1ff, #38e7ff)" },
    { label: "平均响应", value: "95", unit: "ms", percent: 80, color: "#a855f7", gradient: "linear-gradient(90deg, #a855f7, #c084fc)" },
    { label: "拦截成功率", value: "98.0", unit: "%", percent: 98, color: "#22d3a5", gradient: "linear-gradient(90deg, #22d3a5, #7ff3d1)" },
    { label: "设备稳定度", value: availability.toFixed(1), unit: "%", percent: Math.min(100, availability), color: "#f5a524", gradient: "linear-gradient(90deg, #f5a524, #ffd08a)" },
  ];
});

const pointData = computed(() =>
  devices.value.slice(0, 40).map((d, idx) => {
    const row = Math.floor(idx / 8);
    const col = idx % 8;
    const lat = 39.89 + row * 0.01 + col * 0.001;
    const lng = 116.37 + col * 0.01 + row * 0.001;
    const status =
      d.status === "triggered" || d.status === "cutoff"
        ? "alert"
        : d.status === "offline"
          ? "warn"
          : "normal";
    const statusText = status === "alert" ? "告警" : status === "warn" ? "异常" : "正常";
    return {
      deviceId: d.id,
      name: d.name || d.id,
      status,
      statusText,
      position: d.location || "--",
      lastHeartbeat: d.last_seen ? String(d.last_seen).replace("T", " ").slice(0, 19) : "--",
      lat,
      lng,
    };
  })
);

const createDivIcon = (status) =>
  L.divIcon({
    className: "map-marker-wrapper",
    html: `<span class="marker-ring marker-ring--${status}"></span><span class="marker-core marker-core--${status}"></span>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });

const renderMarkers = () => {
  if (!leafletMap.value) return;
  leafletMap.value.eachLayer((layer) => {
    if (layer instanceof L.Marker) leafletMap.value.removeLayer(layer);
  });
  pointData.value.forEach((point) => {
    const marker = L.marker([point.lat, point.lng], { icon: createDivIcon(point.status) }).addTo(leafletMap.value);
    marker.on("click", () => {
      selectedDevice.value = point;
      deviceDialogVisible.value = true;
    });
  });
};

const initMap = () => {
  if (!mapContainer.value || leafletMap.value) return;
  leafletMap.value = L.map(mapContainer.value, { zoomControl: true, attributionControl: false }).setView([39.907, 116.395], 13);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { subdomains: "abcd", maxZoom: 20 }).addTo(leafletMap.value);
  renderMarkers();
};

const loadDashboardData = async () => {
  try {
    const [devicesData, eventsData, statsData] = await Promise.all([
      getDevices({ limit: 500 }),
      getEvents({ limit: 200 }),
      getStatistics(),
    ]);
    devices.value = Array.isArray(devicesData) ? devicesData : [];
    events.value = Array.isArray(eventsData) ? eventsData : [];
    statistics.value = statsData;
    renderMarkers();
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "加载仪表盘数据失败");
  }
};

const handleRemoteReset = async () => {
  if (!selectedDevice.value) return;
  try {
    await sendControl(selectedDevice.value.deviceId, "reset");
    ElMessage.success(`设备 ${selectedDevice.value.deviceId} 已下发远程复位指令`);
    deviceDialogVisible.value = false;
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "复位指令发送失败");
  }
};

onMounted(async () => {
  initMap();
  await loadDashboardData();
});

onBeforeUnmount(() => {
  if (leafletMap.value) {
    leafletMap.value.remove();
    leafletMap.value = null;
  }
});
</script>

<style scoped lang="scss">
.dashboard-page {
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
  letter-spacing: 0.16em;
  margin-bottom: 6px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);

  h3 {
    margin: 0;
    color: #f1f5f9;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
}

.legend {
  display: flex;
  gap: 14px;
  color: #94a3b8;
  font-size: 12px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-green {
  background: #22d3a5;
  box-shadow: 0 0 10px rgba(34, 211, 165, 0.8);
}
.dot-orange {
  background: #f5a524;
  box-shadow: 0 0 10px rgba(245, 165, 36, 0.8);
}
.dot-red {
  background: #ff5470;
  box-shadow: 0 0 10px rgba(255, 84, 112, 0.8);
}
.dot-cyan {
  background: #00d1ff;
  box-shadow: 0 0 10px rgba(0, 209, 255, 0.8);
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.kpi-card {
  position: relative;
  padding: 18px 20px;
  border-radius: 18px;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 209, 255, 0.35) !important;
}

.kpi-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kpi-label {
  color: #94a3b8;
  font-size: 13px;
  letter-spacing: 0.04em;
}

.kpi-trend {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  font-family: var(--font-family-mono);
}

.kpi-trend.up {
  color: #7ff3d1;
  background: rgba(34, 211, 165, 0.1);
  border: 1px solid rgba(34, 211, 165, 0.35);
}

.kpi-trend.down {
  color: #ffb3c1;
  background: rgba(255, 84, 112, 0.1);
  border: 1px solid rgba(255, 84, 112, 0.4);
}

.kpi-value-line {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 12px;
}

.kpi-value {
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0.02em;
  font-family: var(--font-family-mono);
}

.kpi-unit {
  color: #64748b;
  font-size: 13px;
}

.kpi-card.tone-cyan .kpi-value {
  color: #00d1ff;
  text-shadow: 0 0 14px rgba(0, 209, 255, 0.45);
}
.kpi-card.tone-violet .kpi-value {
  color: #c084fc;
  text-shadow: 0 0 14px rgba(168, 85, 247, 0.45);
}
.kpi-card.tone-warn .kpi-value {
  color: #f5a524;
  text-shadow: 0 0 14px rgba(245, 165, 36, 0.45);
}
.kpi-card.tone-danger .kpi-value {
  color: #ff5470;
  text-shadow: 0 0 14px rgba(255, 84, 112, 0.45);
}

.kpi-spark {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 32px;
}

.kpi-spark .bar {
  flex: 1;
  border-radius: 3px 3px 0 0;
  background: linear-gradient(180deg, rgba(0, 209, 255, 0.65), rgba(0, 209, 255, 0.1));
  opacity: 0.85;
  transition: height 0.3s ease;
}

.kpi-card.tone-violet .kpi-spark .bar {
  background: linear-gradient(180deg, rgba(168, 85, 247, 0.7), rgba(168, 85, 247, 0.1));
}
.kpi-card.tone-warn .kpi-spark .bar {
  background: linear-gradient(180deg, rgba(245, 165, 36, 0.7), rgba(245, 165, 36, 0.1));
}
.kpi-card.tone-danger .kpi-spark .bar {
  background: linear-gradient(180deg, rgba(255, 84, 112, 0.75), rgba(255, 84, 112, 0.1));
}

.kpi-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.7;
}

.kpi-card.tone-cyan .kpi-glow {
  background: radial-gradient(160px 100px at 100% 0%, rgba(0, 209, 255, 0.18), transparent 70%);
}
.kpi-card.tone-violet .kpi-glow {
  background: radial-gradient(160px 100px at 100% 0%, rgba(168, 85, 247, 0.18), transparent 70%);
}
.kpi-card.tone-warn .kpi-glow {
  background: radial-gradient(160px 100px at 100% 0%, rgba(245, 165, 36, 0.16), transparent 70%);
}
.kpi-card.tone-danger .kpi-glow {
  background: radial-gradient(160px 100px at 100% 0%, rgba(255, 84, 112, 0.2), transparent 70%);
}

.middle-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 14px;
}

.map-card,
.events-card {
  border-radius: 18px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.map-card {
  position: relative;
  min-height: 460px;
}

.map-container {
  flex: 1;
  min-height: 420px;
}

.map-overlay-tr {
  position: absolute;
  right: 16px;
  top: 80px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(12, 13, 18, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 150px;
}

.overlay-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
}

.overlay-row .label {
  color: #94a3b8;
}

.overlay-row .value {
  font-family: var(--font-family-mono);
  color: #e2e8f0;
}

.events-card {
  min-height: 460px;
}

.live {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #ff5470;
  font-size: 12px;
  letter-spacing: 0.2em;
  font-family: var(--font-family-mono);
}

.live .pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff5470;
  box-shadow: 0 0 10px rgba(255, 84, 112, 0.85);
  animation: pulse 1.4s infinite;
}

.event-stream {
  list-style: none;
  margin: 0;
  padding: 12px 16px;
  overflow-y: auto;
  max-height: 420px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.event-item {
  display: flex;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.025);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.event-item:hover {
  border-color: rgba(0, 209, 255, 0.35);
  background: rgba(0, 209, 255, 0.05);
}

.event-item.danger {
  border-color: rgba(255, 84, 112, 0.45);
  background: rgba(255, 84, 112, 0.06);
}

.event-item .time {
  width: 64px;
  flex-shrink: 0;
  color: #64748b;
  font-family: var(--font-family-mono);
  font-size: 12px;
  padding-top: 2px;
}

.event-item .content {
  flex: 1;
  min-width: 0;
}

.row-1 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.device-id {
  color: #e2e8f0;
  font-weight: 600;
}

.row-2 {
  color: #94a3b8;
  font-size: 12px;
}

.row-2 .sep {
  margin: 0 6px;
  color: #475569;
}

.bottom-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 14px;
}

.activity-card,
.summary-card {
  border-radius: 18px;
  overflow: hidden;
}

.heatmap {
  padding: 18px 20px;
  display: grid;
  grid-template-columns: repeat(24, 1fr);
  gap: 6px;
}

.heatmap .cell {
  position: relative;
  aspect-ratio: 1;
  border-radius: 6px;
  background: rgba(0, 209, 255, calc(var(--h) * 0.8));
  box-shadow: 0 0 calc(var(--h) * 14px) rgba(0, 209, 255, calc(var(--h) * 0.45));
  border: 1px solid rgba(0, 209, 255, calc(var(--h) * 0.5));
  transition: transform 0.2s ease;
}

.heatmap .cell em {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-style: normal;
  font-size: 10px;
  font-family: var(--font-family-mono);
  color: rgba(255, 255, 255, 0.7);
  opacity: 0.7;
}

.heatmap .cell:hover {
  transform: scale(1.15);
  z-index: 1;
}

.metric-list {
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.m-head {
  display: flex;
  justify-content: space-between;
  color: #cbd5e1;
  font-size: 13px;
}

.m-value {
  font-family: var(--font-family-mono);
  font-weight: 600;
  text-shadow: 0 0 10px currentColor;
  filter: brightness(1.1);
}

.m-bar {
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.m-bar span {
  display: block;
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
  box-shadow: 0 0 12px rgba(0, 209, 255, 0.35);
}

.device-detail {
  display: grid;
  gap: 10px;
}

.device-detail p {
  display: flex;
  justify-content: space-between;
  margin: 0;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
}

.device-detail p:last-child {
  border-bottom: none;
}

.device-detail span {
  color: #94a3b8;
}

.device-detail strong {
  color: #e2e8f0;
  font-weight: 500;
}

:deep(.leaflet-container) {
  background: #05070d;
}

:deep(.leaflet-control-zoom a) {
  background: rgba(12, 13, 18, 0.85);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(6px);
}

:deep(.leaflet-control-zoom a:hover) {
  color: #00d1ff;
  border-color: rgba(0, 209, 255, 0.5) !important;
}

:deep(.map-marker-wrapper) {
  position: relative;
}

:deep(.marker-core) {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.9);
}

:deep(.marker-core--normal) {
  background: #22d3a5;
  box-shadow: 0 0 14px rgba(34, 211, 165, 0.8);
}

:deep(.marker-core--warn) {
  background: #f5a524;
  box-shadow: 0 0 14px rgba(245, 165, 36, 0.8);
}

:deep(.marker-core--alert) {
  background: #ff5470;
  box-shadow: 0 0 14px rgba(255, 84, 112, 0.9);
}

:deep(.marker-ring) {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  pointer-events: none;
}

:deep(.marker-ring--normal) {
  box-shadow: 0 0 0 0 rgba(34, 211, 165, 0.55);
  animation: ring-pulse 2s infinite;
  animation-name: ring-green;
}

:deep(.marker-ring--warn) {
  animation: ring-pulse 2s infinite;
  animation-name: ring-orange;
}

:deep(.marker-ring--alert) {
  animation: ring-pulse 1.4s infinite;
  animation-name: ring-red;
}

@keyframes ring-green {
  0% { box-shadow: 0 0 0 0 rgba(34, 211, 165, 0.7); }
  70% { box-shadow: 0 0 0 18px rgba(34, 211, 165, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 211, 165, 0); }
}
@keyframes ring-orange {
  0% { box-shadow: 0 0 0 0 rgba(245, 165, 36, 0.7); }
  70% { box-shadow: 0 0 0 18px rgba(245, 165, 36, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 165, 36, 0); }
}
@keyframes ring-red {
  0% { box-shadow: 0 0 0 0 rgba(255, 84, 112, 0.8); }
  70% { box-shadow: 0 0 0 20px rgba(255, 84, 112, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 84, 112, 0); }
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.5; }
}

@media (max-width: 1200px) {
  .middle-row,
  .bottom-row {
    grid-template-columns: 1fr;
  }
  .kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
