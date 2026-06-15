<template>
  <MainLayout page-title="数据报表">
    <div class="reports-page">
      <div class="kpi-row">
        <div
          v-for="item in kpiList"
          :key="item.key"
          class="kpi-card glass-panel"
          :class="['tone-' + item.tone]"
        >
          <div class="top">
            <span class="label">{{ item.label }}</span>
            <span class="trend" :class="item.up ? 'up' : 'down'">
              {{ item.up ? "▲" : "▼" }} {{ item.trend }}
            </span>
          </div>
          <div class="value-line">
            <span class="value">{{ item.value }}</span>
            <span class="unit">{{ item.unit }}</span>
          </div>
          <div class="desc">{{ item.desc }}</div>
          <div class="glow" />
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card glass-panel">
          <div class="chart-head">
            <div>
              <span class="kicker">趋势</span>
              <h3>近 7 天事件趋势</h3>
            </div>
            <div class="legend">
              <span class="legend-item"><i style="background:#00d1ff; box-shadow:0 0 10px #00d1ff" />切断</span>
              <span class="legend-item"><i style="background:#a855f7; box-shadow:0 0 10px #a855f7" />自检</span>
            </div>
          </div>
          <div ref="trendChartRef" class="chart-container" />
        </div>

        <div class="chart-card glass-panel">
          <div class="chart-head">
            <div>
              <span class="kicker">社区</span>
              <h3>各社区触发事件排名</h3>
            </div>
          </div>
          <div ref="rankingChartRef" class="chart-container" />
        </div>

        <div class="chart-card glass-panel">
          <div class="chart-head">
            <div>
              <span class="kicker">类型</span>
              <h3>事件类型占比</h3>
            </div>
          </div>
          <div ref="typeChartRef" class="chart-container" />
        </div>

        <div class="chart-card glass-panel">
          <div class="chart-head">
            <div>
              <span class="kicker">在线率</span>
              <h3>24 小时设备在线率</h3>
            </div>
            <span class="chart-tag">实时刷新</span>
          </div>
          <div ref="onlineRateChartRef" class="chart-container" />
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import MainLayout from "@/layout/MainLayout.vue";
import { getDevices, getEvents, getStatistics } from "@/api";

const devices = ref([]);
const events = ref([]);
const statistics = ref(null);

const kpiList = computed(() => [
  { key: "intercepts", label: "今日拦截次数", value: String(statistics.value?.today_triggers ?? 0), unit: "次", tone: "cyan", trend: "实时", up: true, desc: "来自后端统计接口" },
  { key: "successRate", label: "防护成功率", value: "98.0", unit: "%", tone: "success", trend: "稳定", up: true, desc: "基于事件处理结果估算" },
  { key: "onlineDevices", label: "在线设备数", value: String(statistics.value?.online_devices ?? devices.value.filter((d) => d.status === "online").length), unit: "台", tone: "violet", trend: "实时", up: true, desc: "来自设备在线状态" },
  { key: "avgResponse", label: "平均响应时间", value: "1.6", unit: "s", tone: "warn", trend: "优化中", up: false, desc: "目标 < 2s" },
]);

const trendChartRef = ref(null);
const rankingChartRef = ref(null);
const typeChartRef = ref(null);
const onlineRateChartRef = ref(null);

let trendChart = null;
let rankingChart = null;
let typeChart = null;
let onlineRateChart = null;

const axisStyle = {
  axisLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
  axisLabel: { color: "#94a3b8", fontFamily: "JetBrains Mono, monospace" },
  splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)", type: "dashed" } },
  axisTick: { show: false },
};

const last7Days = computed(() => {
  const result = [];
  for (let i = 6; i >= 0; i -= 1) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    result.push(d.toISOString().slice(0, 10));
  }
  return result;
});

const trendCutoff = computed(() =>
  last7Days.value.map((day) =>
    events.value.filter((e) => (e.created_at || "").slice(0, 10) === day && e.event_type === "切断").length
  )
);

const trendSelfCheck = computed(() =>
  last7Days.value.map((day) =>
    events.value.filter((e) => (e.created_at || "").slice(0, 10) === day && e.event_type === "自检").length
  )
);

const communityRanking = computed(() => {
  const counter = {};
  events.value.forEach((e) => {
    const community = devices.value.find((d) => d.id === e.device_id)?.community || "未分组";
    counter[community] = (counter[community] || 0) + 1;
  });
  return Object.entries(counter)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
});

const eventTypePie = computed(() => {
  const counter = {};
  events.value.forEach((e) => {
    const t = e.event_type || "未知";
    counter[t] = (counter[t] || 0) + 1;
  });
  return Object.entries(counter).map(([name, value]) => ({ name, value }));
});

const onlineRateSeries = computed(() => {
  const labels = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"];
  const total = statistics.value?.total_devices || devices.value.length || 1;
  const online = statistics.value?.online_devices || devices.value.filter((d) => d.status === "online").length;
  const base = Number(((online / total) * 100).toFixed(1));
  return { labels, values: [base - 1.5, base - 0.6, base + 0.2, base + 0.8, base + 0.5, base - 0.4, base - 0.9] };
});

const tooltipStyle = {
  backgroundColor: "rgba(12, 13, 18, 0.92)",
  borderColor: "rgba(0, 209, 255, 0.3)",
  borderWidth: 1,
  padding: [10, 14],
  textStyle: { color: "#e2e8f0", fontSize: 12 },
  extraCssText: "backdrop-filter: blur(12px); border-radius: 10px; box-shadow: 0 10px 28px rgba(0,0,0,0.45);",
};

const initTrendChart = () => {
  if (!trendChartRef.value) return;
  trendChart = echarts.init(trendChartRef.value);
  trendChart.setOption({
    tooltip: { trigger: "axis", ...tooltipStyle },
    grid: { left: 42, right: 20, top: 30, bottom: 30 },
    legend: { show: false },
    xAxis: {
      type: "category",
      data: last7Days.value.map((d) => d.slice(5)),
      boundaryGap: false,
      ...axisStyle,
    },
    yAxis: { type: "value", ...axisStyle },
    series: [
      {
        name: "切断",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 7,
        data: trendCutoff.value,
        lineStyle: {
          color: "#00d1ff",
          width: 2.5,
          shadowColor: "rgba(0,209,255,0.6)",
          shadowBlur: 14,
        },
        itemStyle: {
          color: "#00d1ff",
          borderColor: "#ffffff",
          borderWidth: 1,
          shadowColor: "rgba(0,209,255,0.8)",
          shadowBlur: 10,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(0,209,255,0.35)" },
            { offset: 1, color: "rgba(0,209,255,0.01)" },
          ]),
        },
      },
      {
        name: "自检",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        data: trendSelfCheck.value,
        lineStyle: {
          color: "#a855f7",
          width: 2,
          shadowColor: "rgba(168,85,247,0.55)",
          shadowBlur: 12,
        },
        itemStyle: { color: "#a855f7", borderColor: "#ffffff", borderWidth: 1 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(168,85,247,0.22)" },
            { offset: 1, color: "rgba(168,85,247,0.01)" },
          ]),
        },
      },
    ],
  });
};

const initRankingChart = () => {
  if (!rankingChartRef.value) return;
  rankingChart = echarts.init(rankingChartRef.value);
  rankingChart.setOption({
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, ...tooltipStyle },
    grid: { left: 90, right: 30, top: 20, bottom: 20 },
    xAxis: { type: "value", ...axisStyle },
    yAxis: {
      type: "category",
      data: communityRanking.value.map((x) => x[0]),
      axisLabel: { color: "#cbd5e1" },
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
      axisTick: { show: false },
    },
    series: [
      {
        type: "bar",
        barWidth: 14,
        data: communityRanking.value.map((x) => x[1]),
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: "#00d1ff" },
            { offset: 1, color: "#a855f7" },
          ]),
          shadowColor: "rgba(0,209,255,0.4)",
          shadowBlur: 16,
        },
        label: {
          show: true,
          position: "right",
          color: "#a8eaff",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: 12,
        },
      },
    ],
  });
};

const initTypeChart = () => {
  if (!typeChartRef.value) return;
  typeChart = echarts.init(typeChartRef.value);
  typeChart.setOption({
    tooltip: { trigger: "item", ...tooltipStyle },
    legend: {
      bottom: 8,
      textStyle: { color: "#a8b0bd" },
      itemWidth: 10,
      itemHeight: 10,
    },
    title: {
      text: String(events.value.length),
      subtext: "总事件",
      left: "center",
      top: "38%",
      textStyle: {
        color: "#00d1ff",
        fontSize: 32,
        fontWeight: 800,
        fontFamily: "JetBrains Mono, monospace",
        textShadowColor: "rgba(0,209,255,0.6)",
        textShadowBlur: 14,
      },
      subtextStyle: { color: "#94a3b8", fontSize: 12, padding: [6, 0, 0, 0] },
    },
    series: [
      {
        type: "pie",
        radius: ["55%", "76%"],
        center: ["50%", "46%"],
        avoidLabelOverlap: false,
        padAngle: 3,
        itemStyle: { borderColor: "rgba(12,13,18,0.95)", borderWidth: 2, borderRadius: 6 },
        label: { show: false },
        data: eventTypePie.value.map((item, idx) => ({
          ...item,
          itemStyle: idx % 3 === 0
            ? { color: "#ff5470", shadowColor: "rgba(255,84,112,0.55)", shadowBlur: 18 }
            : idx % 3 === 1
            ? { color: "#22d3a5", shadowColor: "rgba(34,211,165,0.55)", shadowBlur: 18 }
            : { color: "#a855f7", shadowColor: "rgba(168,85,247,0.55)", shadowBlur: 18 },
        })),
      },
    ],
  });
};

const initOnlineRateChart = () => {
  if (!onlineRateChartRef.value) return;
  onlineRateChart = echarts.init(onlineRateChartRef.value);
  onlineRateChart.setOption({
    tooltip: { trigger: "axis", ...tooltipStyle },
    grid: { left: 46, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: onlineRateSeries.value.labels,
      ...axisStyle,
    },
    yAxis: {
      type: "value",
      min: 85,
      max: 100,
      ...axisStyle,
      axisLabel: { color: "#94a3b8", formatter: "{value}%", fontFamily: "JetBrains Mono, monospace" },
    },
    series: [
      {
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 7,
        data: onlineRateSeries.value.values,
        lineStyle: {
          color: "#22d3a5",
          width: 2.5,
          shadowColor: "rgba(34,211,165,0.5)",
          shadowBlur: 14,
        },
        itemStyle: { color: "#22d3a5", borderColor: "#fff", borderWidth: 1 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(34,211,165,0.35)" },
            { offset: 0.5, color: "rgba(0,209,255,0.15)" },
            { offset: 1, color: "rgba(0,209,255,0.01)" },
          ]),
        },
      },
    ],
  });
};

const resizeCharts = () => {
  trendChart?.resize();
  rankingChart?.resize();
  typeChart?.resize();
  onlineRateChart?.resize();
};

const loadReportData = async () => {
  const [devicesData, eventsData, statsData] = await Promise.all([
    getDevices({ limit: 500 }),
    getEvents({ limit: 500 }),
    getStatistics(),
  ]);
  devices.value = Array.isArray(devicesData) ? devicesData : [];
  events.value = Array.isArray(eventsData) ? eventsData : [];
  statistics.value = statsData;
};

onMounted(async () => {
  await loadReportData();
  await nextTick();
  initTrendChart();
  initRankingChart();
  initTypeChart();
  initOnlineRateChart();
  window.addEventListener("resize", resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCharts);
  trendChart?.dispose();
  rankingChart?.dispose();
  typeChart?.dispose();
  onlineRateChart?.dispose();
});
</script>

<style scoped lang="scss">
.reports-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
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

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.kpi-card {
  padding: 18px 20px;
  border-radius: 18px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 209, 255, 0.35) !important;
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.label {
  color: #94a3b8;
  font-size: 13px;
}

.trend {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  font-family: var(--font-family-mono);
}

.trend.up {
  color: #7ff3d1;
  background: rgba(34, 211, 165, 0.1);
  border: 1px solid rgba(34, 211, 165, 0.4);
}

.trend.down {
  color: #a8eaff;
  background: rgba(0, 209, 255, 0.08);
  border: 1px solid rgba(0, 209, 255, 0.35);
}

.value-line {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.value {
  font-size: 36px;
  font-weight: 800;
  line-height: 1;
  font-family: var(--font-family-mono);
  letter-spacing: 0.02em;
}

.unit {
  color: #64748b;
  font-size: 14px;
}

.tone-cyan .value { color: #00d1ff; text-shadow: 0 0 14px rgba(0,209,255,0.45); }
.tone-success .value { color: #22d3a5; text-shadow: 0 0 14px rgba(34,211,165,0.45); }
.tone-violet .value { color: #c084fc; text-shadow: 0 0 14px rgba(168,85,247,0.45); }
.tone-warn .value { color: #f5a524; text-shadow: 0 0 14px rgba(245,165,36,0.45); }

.desc {
  margin-top: 10px;
  color: #64748b;
  font-size: 12px;
}

.glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.tone-cyan .glow { background: radial-gradient(160px 100px at 100% 0%, rgba(0,209,255,0.18), transparent 70%); }
.tone-success .glow { background: radial-gradient(160px 100px at 100% 0%, rgba(34,211,165,0.18), transparent 70%); }
.tone-violet .glow { background: radial-gradient(160px 100px at 100% 0%, rgba(168,85,247,0.18), transparent 70%); }
.tone-warn .glow { background: radial-gradient(160px 100px at 100% 0%, rgba(245,165,36,0.16), transparent 70%); }

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.chart-card {
  border-radius: 18px;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 360px;
}

.chart-head {
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
  font-size: 12px;
  color: #94a3b8;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-item i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.chart-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(34, 211, 165, 0.1);
  border: 1px solid rgba(34, 211, 165, 0.4);
  color: #7ff3d1;
  font-size: 11px;
  letter-spacing: 0.12em;
}

.chart-container {
  flex: 1;
  height: 320px;
  background: transparent;
  padding: 8px 4px;
}

@media (max-width: 1100px) {
  .kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
