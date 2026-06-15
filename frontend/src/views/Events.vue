<template>
  <MainLayout page-title="事件记录">
    <div class="events-page">
      <div class="stat-row">
        <div
          v-for="s in stats"
          :key="s.key"
          class="stat-card glass-panel"
          :class="'tone-' + s.tone"
        >
          <div class="stat-head">
            <span class="icon">{{ s.icon }}</span>
            <span>{{ s.label }}</span>
          </div>
          <div class="stat-value">{{ s.value }}<em>{{ s.unit }}</em></div>
          <div class="stat-bar">
            <span :style="{ width: s.percent + '%' }" />
          </div>
        </div>
      </div>

      <div class="filter-card glass-panel">
        <div class="filter-inner">
          <el-form inline>
            <el-form-item label="设备ID">
              <el-input
                v-model="filters.deviceId"
                placeholder="请输入设备ID"
                clearable
                style="width: 180px"
              />
            </el-form-item>
            <el-form-item label="事件类型">
              <el-select v-model="filters.type" placeholder="请选择类型" style="width: 140px">
                <el-option label="全部类型" value="all" />
                <el-option label="切断" value="切断" />
                <el-option label="恢复" value="恢复" />
                <el-option label="自检" value="自检" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="filters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button plain @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="export-wrap">
          <el-button type="primary" @click="handleExport">
            <span>导 出 CSV</span>
          </el-button>
        </div>
      </div>

      <div class="table-card glass-panel">
        <div class="table-head">
          <div>
            <span class="kicker">事件流</span>
            <h3>全量事件记录</h3>
          </div>
          <div class="legend">
            <span class="legend-item danger"><i />切断</span>
            <span class="legend-item success"><i />恢复</span>
            <span class="legend-item info"><i />自检</span>
          </div>
        </div>
        <el-table :data="paginatedEvents" stripe>
          <el-table-column label="时间" min-width="180">
            <template #default="{ row }">
              <span class="text-mono cell-time">{{ row.time }}</span>
            </template>
          </el-table-column>
          <el-table-column label="设备ID" width="130">
            <template #default="{ row }">
              <span class="text-mono cell-id">{{ row.deviceId }}</span>
            </template>
          </el-table-column>
          <el-table-column label="事件类型" width="110">
            <template #default="{ row }">
              <el-tag :type="getTagType(row.type)">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="峰值加速度" width="180">
            <template #default="{ row }">
              <div class="pga-cell">
                <span class="pga-value" :class="getPgaClass(row.pga)">{{ row.pga }}</span>
                <span class="pga-bar">
                  <i :style="{ width: getPgaPct(row.pga) + '%', background: getPgaGradient(row.pga) }" />
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" min-width="160" />
          <el-table-column prop="community" label="社区" min-width="130" />
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" @click="openDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrap">
        <span class="count">
          共 <strong>{{ filteredEvents.length }}</strong> 条事件
        </span>
        <el-pagination
          layout="prev, pager, next"
          :total="filteredEvents.length"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="(page) => (currentPage = page)"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="事件详情" width="640px">
      <div v-if="selectedEvent" class="detail-head">
        <div class="d-item">
          <span>设备</span>
          <strong class="text-mono">{{ selectedEvent.deviceId }}</strong>
        </div>
        <div class="d-item">
          <span>时间</span>
          <strong class="text-mono">{{ selectedEvent.time }}</strong>
        </div>
        <div class="d-item">
          <span>类型</span>
          <el-tag :type="getTagType(selectedEvent.type)">{{ selectedEvent.type }}</el-tag>
        </div>
        <div class="d-item">
          <span>峰值</span>
          <strong :class="getPgaClass(selectedEvent.pga)">{{ selectedEvent.pga }}</strong>
        </div>
      </div>
      <pre class="json-view">{{ selectedEventJson }}</pre>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="detailVisible = false">知道了</el-button>
      </template>
    </el-dialog>
  </MainLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import MainLayout from "@/layout/MainLayout.vue";
import { exportEvents, getDevices, getEvents } from "@/api";

/** 筛选下拉与后端 event_type 对应 */
const FILTER_TYPE_TO_API = {
  切断: "shutdown",
  恢复: "restore",
  自检: "check",
};

const EVENT_TYPE_LABELS = {
  shutdown: "切断",
  restore: "恢复",
  check: "自检",
  heartbeat: "心跳",
};

const pageSize = 8;
const currentPage = ref(1);
const filters = reactive({ deviceId: "", type: "all", dateRange: [] });

const allEvents = ref([]);
const allDevices = ref([]);

const normalizeEvent = (item) => {
  const raw = item.event_type || "";
  return {
    id: item.id,
    time: item.created_at ? String(item.created_at).replace("T", " ").slice(0, 19) : "--",
    deviceId: item.device_id,
    rawType: raw,
    type: EVENT_TYPE_LABELS[raw] || raw || "未知",
    pga: item.acc_max === null || item.acc_max === undefined ? "--" : `${item.acc_max}g`,
    location: allDevices.value.find((d) => d.id === item.device_id)?.location || "--",
    community: allDevices.value.find((d) => d.id === item.device_id)?.community || "--",
  };
};

const stats = computed(() => {
  const total = allEvents.value.length;
  const cutoff = allEvents.value.filter((e) => e.rawType === "shutdown").length;
  const restore = allEvents.value.filter((e) => e.rawType === "restore").length;
  const selfCheck = allEvents.value.filter((e) => e.rawType === "check").length;
  const totalSafe = total || 1;
  return [
    { key: "total", icon: "Σ", label: "今日事件", value: total, unit: "条", tone: "cyan", percent: 100 },
    { key: "cutoff", icon: "!", label: "切断事件", value: cutoff, unit: "次", tone: "danger", percent: (cutoff / totalSafe) * 100 },
    { key: "restore", icon: "✓", label: "恢复事件", value: restore, unit: "次", tone: "success", percent: (restore / totalSafe) * 100 },
    { key: "selfCheck", icon: "↻", label: "自检事件", value: selfCheck, unit: "次", tone: "violet", percent: (selfCheck / totalSafe) * 100 },
  ];
});

const filteredEvents = computed(() => {
  const keyword = filters.deviceId.trim().toLowerCase();
  return allEvents.value.filter((item) => {
    const deviceMatch = !keyword || item.deviceId.toLowerCase().includes(keyword);
    const typeMatch = filters.type === "all" || item.type === filters.type;
    let dateMatch = true;
    if (Array.isArray(filters.dateRange) && filters.dateRange.length === 2) {
      const [start, end] = filters.dateRange;
      const day = item.time.slice(0, 10);
      dateMatch = day >= start && day <= end;
    }
    return deviceMatch && typeMatch && dateMatch;
  });
});

const paginatedEvents = computed(() =>
  filteredEvents.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
);

const detailVisible = ref(false);
const selectedEvent = ref(null);
const selectedEventJson = computed(() => JSON.stringify(selectedEvent.value ?? {}, null, 2));

const fetchEvents = async () => {
  try {
    const devicesData = await getDevices({ limit: 500 });
    allDevices.value = Array.isArray(devicesData) ? devicesData : [];

    const params = {};
    if (filters.deviceId.trim()) params.device_id = filters.deviceId.trim();
    if (filters.type !== "all") params.event_type = FILTER_TYPE_TO_API[filters.type] ?? filters.type;
    if (Array.isArray(filters.dateRange) && filters.dateRange.length === 2) {
      params.start_time = `${filters.dateRange[0]}T00:00:00`;
      params.end_time = `${filters.dateRange[1]}T23:59:59`;
    }
    const data = await getEvents({ ...params, limit: 500 });
    allEvents.value = Array.isArray(data) ? data.map(normalizeEvent) : [];
    currentPage.value = 1;
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "获取事件记录失败");
  }
};

const handleSearch = () => { fetchEvents(); };
const handleReset = () => {
  filters.deviceId = "";
  filters.type = "all";
  filters.dateRange = [];
  fetchEvents();
};
const handleExport = async () => {
  try {
    const params = {};
    if (filters.deviceId.trim()) params.device_id = filters.deviceId.trim();
    if (filters.type !== "all") params.event_type = FILTER_TYPE_TO_API[filters.type] ?? filters.type;
    if (Array.isArray(filters.dateRange) && filters.dateRange.length === 2) {
      params.start_time = `${filters.dateRange[0]}T00:00:00`;
      params.end_time = `${filters.dateRange[1]}T23:59:59`;
    }
    const blob = await exportEvents({ ...params, limit: 500 });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "events.csv";
    a.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "导出失败");
  }
};
const getTagType = (type) => (type === "切断" ? "danger" : type === "恢复" ? "success" : "info");
const openDetail = (row) => { selectedEvent.value = row; detailVisible.value = true; };

const parsePga = (s) => parseFloat(String(s).replace("g", "")) || 0;
const getPgaClass = (pga) => {
  const v = parsePga(pga);
  if (v >= 3.5) return "high";
  if (v >= 2) return "mid";
  return "low";
};
const getPgaPct = (pga) => Math.min(100, Math.max(8, (parsePga(pga) / 5) * 100));
const getPgaGradient = (pga) => {
  const v = parsePga(pga);
  if (v >= 3.5) return "linear-gradient(90deg,#ff5470,#f87171)";
  if (v >= 2) return "linear-gradient(90deg,#f5a524,#fbbf24)";
  return "linear-gradient(90deg,#00d1ff,#22d3a5)";
};

onMounted(() => {
  fetchEvents();
});
</script>

<style scoped lang="scss">
.events-page {
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

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.stat-card {
  padding: 16px 18px;
  border-radius: 18px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 209, 255, 0.35) !important;
}

.stat-head {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 13px;
  margin-bottom: 10px;
}

.stat-head .icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-family: var(--font-family-mono);
  font-weight: 800;
  font-size: 14px;
}

.tone-cyan .icon { background: rgba(0,209,255,0.1); color: #00d1ff; border: 1px solid rgba(0,209,255,0.35); }
.tone-success .icon { background: rgba(34,211,165,0.1); color: #22d3a5; border: 1px solid rgba(34,211,165,0.35); }
.tone-warn .icon,
.tone-violet .icon { background: rgba(168,85,247,0.12); color: #c084fc; border: 1px solid rgba(168,85,247,0.4); }
.tone-danger .icon { background: rgba(255,84,112,0.12); color: #ff5470; border: 1px solid rgba(255,84,112,0.45); }

.stat-value {
  font-size: 32px;
  font-weight: 800;
  font-family: var(--font-family-mono);
  line-height: 1;
  letter-spacing: 0.02em;
  color: #f1f5f9;
}

.tone-cyan .stat-value { color: #00d1ff; text-shadow: 0 0 14px rgba(0,209,255,0.45); }
.tone-success .stat-value { color: #22d3a5; text-shadow: 0 0 14px rgba(34,211,165,0.45); }
.tone-violet .stat-value { color: #c084fc; text-shadow: 0 0 14px rgba(168,85,247,0.45); }
.tone-danger .stat-value { color: #ff5470; text-shadow: 0 0 14px rgba(255,84,112,0.45); }

.stat-value em {
  font-style: normal;
  font-size: 12px;
  color: #64748b;
  margin-left: 6px;
  text-shadow: none;
  font-family: var(--font-family-base);
  font-weight: 500;
}

.stat-bar {
  margin-top: 12px;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.stat-bar span {
  display: block;
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.tone-cyan .stat-bar span { background: linear-gradient(90deg,#00d1ff,#38e7ff); box-shadow: 0 0 10px rgba(0,209,255,0.45); }
.tone-success .stat-bar span { background: linear-gradient(90deg,#22d3a5,#7ff3d1); box-shadow: 0 0 10px rgba(34,211,165,0.45); }
.tone-violet .stat-bar span { background: linear-gradient(90deg,#a855f7,#c084fc); box-shadow: 0 0 10px rgba(168,85,247,0.45); }
.tone-danger .stat-bar span { background: linear-gradient(90deg,#ff5470,#f87171); box-shadow: 0 0 10px rgba(255,84,112,0.5); }

.filter-card {
  position: relative;
  padding: 14px 18px;
  padding-right: 140px;
  border-radius: 16px;
}

.filter-inner :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 14px;
}

.export-wrap {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
}

.table-card {
  border-radius: 18px;
  padding: 0 4px 6px;
}

.table-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.table-head h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 16px;
  font-weight: 600;
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

.legend-item.danger i { background: #ff5470; box-shadow: 0 0 8px rgba(255,84,112,0.8); }
.legend-item.success i { background: #22d3a5; box-shadow: 0 0 8px rgba(34,211,165,0.8); }
.legend-item.info i { background: #00d1ff; box-shadow: 0 0 8px rgba(0,209,255,0.8); }

.cell-time {
  color: #cbd5e1;
  font-size: 13px;
}

.cell-id {
  color: #00d1ff;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 209, 255, 0.35);
}

.pga-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pga-value {
  font-family: var(--font-family-mono);
  font-weight: 700;
  width: 44px;
}

.pga-value.high { color: #ff5470; text-shadow: 0 0 10px rgba(255,84,112,0.5); }
.pga-value.mid { color: #fbbf24; }
.pga-value.low { color: #22d3a5; }

.pga-bar {
  flex: 1;
  height: 5px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
  display: inline-block;
  max-width: 100px;
}

.pga-bar i {
  display: block;
  height: 100%;
  border-radius: 3px;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
}

.pagination-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 4px;
}

.count {
  color: #94a3b8;
  font-size: 13px;
}

.count strong {
  color: #00d1ff;
  font-family: var(--font-family-mono);
  margin: 0 4px;
  text-shadow: 0 0 10px rgba(0, 209, 255, 0.4);
}

.detail-head {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 14px;
}

.d-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.d-item span {
  color: #64748b;
  font-size: 11px;
  letter-spacing: 0.1em;
}

.d-item strong {
  color: #e2e8f0;
  font-size: 13px;
}

.d-item strong.high { color: #ff5470; }
.d-item strong.mid { color: #fbbf24; }
.d-item strong.low { color: #22d3a5; }

.json-view {
  margin: 0;
  padding: 16px;
  border-radius: 12px;
  background: rgba(2, 6, 12, 0.75);
  color: #a8eaff;
  max-height: 360px;
  overflow: auto;
  font-family: var(--font-family-mono);
  font-size: 12px;
  border: 1px solid rgba(0, 209, 255, 0.15);
  box-shadow: inset 0 0 20px rgba(0, 209, 255, 0.08);
}

@media (max-width: 1100px) {
  .stat-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .filter-card {
    padding-right: 18px;
  }
  .export-wrap {
    position: static;
    transform: none;
    margin-top: 10px;
  }
}
</style>
