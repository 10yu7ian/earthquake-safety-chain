<template>
  <MainLayout page-title="设备管理">
    <div class="devices-page">
      <div class="overview-row">
        <div
          v-for="s in summary"
          :key="s.key"
          class="sum-card glass-panel"
          :class="['tone-' + s.tone, { active: filters.status === s.key }]"
          @click="applyStatusFilter(s.key)"
        >
          <div class="sum-top">
            <span class="s-label">{{ s.label }}</span>
            <span class="s-dot" />
          </div>
          <div class="s-value">{{ s.value }}<em>台</em></div>
          <div class="s-sub">{{ s.sub }}</div>
        </div>
      </div>

      <div class="filter-bar glass-panel">
        <div class="filter-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索设备ID / 位置 / 社区"
            clearable
            class="filter-item keyword"
          >
            <template #prefix>
              <span class="iconify-dot">⌕</span>
            </template>
          </el-input>
          <el-select v-model="filters.status" class="filter-item status" placeholder="状态">
            <el-option label="全部状态" value="all" />
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="已触发" value="triggered" />
          </el-select>
          <el-select v-model="filters.community" class="filter-item community" placeholder="社区">
            <el-option label="全部社区" value="all" />
            <el-option
              v-for="c in communityOptions"
              :key="c"
              :label="c"
              :value="c"
            />
          </el-select>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button plain @click="handleReset">重置</el-button>
          <el-button plain @click="handleRefresh">刷新</el-button>
        </div>
        <div class="filter-right">
          <div class="view-toggle">
            <button
              :class="{ active: view === 'grid' }"
              @click="view = 'grid'"
            >网格</button>
            <button
              :class="{ active: view === 'table' }"
              @click="view = 'table'"
            >列表</button>
          </div>
          <el-button type="primary" @click="openCreateDialog">+ 新增设备</el-button>
        </div>
      </div>

      <div v-if="view === 'grid'" class="grid-list">
        <div
          v-for="device in paginatedDevices"
          :key="device.id"
          class="device-card glass-panel"
          :class="'status-bg-' + device.status"
        >
          <div class="device-head">
            <div class="d-id">
              <span class="text-mono id">{{ device.id }}</span>
              <span class="name">{{ device.name }}</span>
            </div>
            <div :class="['status-chip', 'chip-' + device.status]">
              <span class="chip-dot" />
              {{ getStatusLabel(device.status) }}
            </div>
          </div>

          <div class="meta-grid">
            <div class="meta">
              <span>位置</span>
              <strong>{{ device.location }}</strong>
            </div>
            <div class="meta">
              <span>社区</span>
              <strong>{{ device.community }}</strong>
            </div>
            <div class="meta">
              <span>最后在线</span>
              <strong class="text-mono">{{ device.lastOnline.slice(5) }}</strong>
            </div>
          </div>

          <div class="gauge-row">
            <div class="gauge">
              <div class="gauge-head">
                <span>电池</span>
                <span :class="{ low: device.battery <= 20 }">{{ device.battery }}%</span>
              </div>
              <div class="gauge-bar">
                <span
                  :style="{
                    width: device.battery + '%',
                    background: device.battery <= 20 ? 'linear-gradient(90deg,#ff5470,#f87171)' : 'linear-gradient(90deg,#22d3a5,#38e7ff)'
                  }"
                />
              </div>
            </div>
            <div class="gauge">
              <div class="gauge-head">
                <span>信号</span>
                <span>{{ device.signal }}%</span>
              </div>
              <div class="gauge-bar">
                <span
                  :style="{
                    width: device.signal + '%',
                    background: 'linear-gradient(90deg,#00d1ff,#a855f7)'
                  }"
                />
              </div>
            </div>
          </div>

          <div class="actions">
            <el-button plain size="small" @click="handleSelfCheck(device)">自检</el-button>
            <el-button
              size="small"
              :type="device.status === 'triggered' ? 'danger' : 'default'"
              :plain="device.status !== 'triggered'"
              @click="handleRemoteReset(device)"
            >远程复位</el-button>
            <el-button text size="small" @click="openEditDialog(device)">编辑</el-button>
          </div>

          <div class="card-glow" />
        </div>
      </div>

      <div v-else class="table-list glass-panel">
        <el-table :data="paginatedDevices" stripe>
          <el-table-column prop="id" label="设备ID" width="120" />
          <el-table-column prop="name" label="名称" min-width="160" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <span :class="['status-chip', 'chip-' + row.status]">
                <span class="chip-dot" />
                {{ getStatusLabel(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" min-width="160" />
          <el-table-column prop="community" label="社区" min-width="130" />
          <el-table-column label="电池" width="110">
            <template #default="{ row }">
              <span :class="{ low: row.battery <= 20 }">{{ row.battery }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="信号" width="90">
            <template #default="{ row }">{{ row.signal }}%</template>
          </el-table-column>
          <el-table-column prop="lastOnline" label="最后在线" min-width="170" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button text size="small" @click="handleSelfCheck(row)">自检</el-button>
              <el-button text size="small" @click="handleRemoteReset(row)">复位</el-button>
              <el-button text size="small" @click="openEditDialog(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrap">
        <div class="count">
          共 <strong>{{ filteredDevices.length }}</strong> 台设备
        </div>
        <el-pagination
          layout="prev, pager, next"
          :total="filteredDevices.length"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="(page) => (currentPage = page)"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增设备' : '编辑设备'" width="460px">
      <el-form label-position="top">
        <el-form-item label="设备ID">
          <el-input v-model="deviceForm.id" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="deviceForm.location" />
        </el-form-item>
        <el-form-item label="社区">
          <el-input v-model="deviceForm.community" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDevice">保存</el-button>
      </template>
    </el-dialog>
  </MainLayout>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import MainLayout from "@/layout/MainLayout.vue";
import {
  createDevice,
  getDevices,
  getEvents,
  getStatistics,
  sendControl,
  updateDevice,
} from "@/api";

const pageSize = 6;
const currentPage = ref(1);
const view = ref("grid");
const filters = reactive({ keyword: "", status: "all", community: "all" });
let autoRefreshTimer = null;

const allDevices = ref([]);
const statsOverview = ref(null);
const recentEventsCount = ref(0);

const numberSeed = (id, min, span) => {
  const s = String(id || "");
  let hash = 0;
  for (let i = 0; i < s.length; i += 1) hash += s.charCodeAt(i);
  return min + (hash % span);
};

const normalizeDevice = (item) => ({
  id: item.id,
  name: item.name || item.id,
  status: item.status || "offline",
  location: item.location || "--",
  community: item.community || "--",
  lastOnline: item.last_seen ? String(item.last_seen).replace("T", " ").slice(0, 19) : "--",
  battery: numberSeed(item.id, 50, 50),
  signal: numberSeed(`${item.id}-sig`, 45, 55),
});

const communityOptions = computed(() => {
  const set = new Set(allDevices.value.map((d) => d.community));
  return Array.from(set);
});

const summary = computed(() => {
  const all = allDevices.value.length;
  const online = allDevices.value.filter((d) => d.status === "online").length;
  const offline = allDevices.value.filter((d) => d.status === "offline").length;
  const triggered = allDevices.value.filter((d) => d.status === "triggered").length;
  const onlineRate = statsOverview.value?.total_devices
    ? Math.round((statsOverview.value.online_devices / statsOverview.value.total_devices) * 100)
    : null;
  return [
    { key: "all", label: "总设备", value: all, sub: `近20条事件 ${recentEventsCount.value}`, tone: "cyan" },
    { key: "online", label: "在线", value: online, sub: onlineRate === null ? "实时心跳正常" : `在线率 ${onlineRate}%`, tone: "success" },
    { key: "offline", label: "离线", value: offline, sub: "请排查网络", tone: "warn" },
    { key: "triggered", label: "已触发", value: triggered, sub: "等待处理", tone: "danger" },
  ];
});

const filteredDevices = computed(() => {
  const keyword = filters.keyword.trim().toLowerCase();
  return allDevices.value.filter((item) => {
    const keywordMatch =
      !keyword ||
      item.id.toLowerCase().includes(keyword) ||
      item.location.toLowerCase().includes(keyword) ||
      item.community.toLowerCase().includes(keyword);
    const statusMatch = filters.status === "all" || item.status === filters.status;
    const communityMatch = filters.community === "all" || item.community === filters.community;
    return keywordMatch && statusMatch && communityMatch;
  });
});

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredDevices.value.slice(start, start + pageSize);
});

const dialogVisible = ref(false);
const dialogMode = ref("create");
const editingDeviceId = ref("");
const deviceForm = reactive({ id: "", location: "", community: "" });

const applyStatusFilter = (key) => {
  filters.status = key;
  fetchDevices({ resetPage: true });
};
const getStatusLabel = (status) =>
  status === "online" ? "在线" : status === "offline" ? "离线" : "已触发";
const fetchDevices = async ({ resetPage = true } = {}) => {
  try {
    const params = {};
    if (filters.status !== "all") params.status = filters.status;
    if (filters.community !== "all") params.community = filters.community;
    const data = await getDevices(params);
    allDevices.value = Array.isArray(data) ? data.map(normalizeDevice) : [];
    if (resetPage) currentPage.value = 1;
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "获取设备列表失败");
  }
};

const fetchOverview = async () => {
  try {
    const [statsData, eventsData] = await Promise.all([
      getStatistics(),
      getEvents({ limit: 20 }),
    ]);
    statsOverview.value = statsData;
    recentEventsCount.value = Array.isArray(eventsData) ? eventsData.length : 0;
  } catch (error) {
    ElMessage.warning(error?.response?.data?.detail || "统计信息获取失败");
  }
};

const handleSelfCheck = async (device) => {
  try {
    await sendControl(device.id, "self_check");
    ElMessage.success(`${device.name} 自检任务已下发`);
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "下发自检指令失败");
  }
};

const handleRemoteReset = async (device) => {
  try {
    await sendControl(device.id, "reset");
    ElMessage.success("复位指令已发送，设备将自动恢复");
    window.setTimeout(() => {
      fetchDevices({ resetPage: false });
    }, 2000);
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "复位指令发送失败");
  }
};
const openCreateDialog = () => {
  dialogMode.value = "create";
  editingDeviceId.value = "";
  deviceForm.id = "";
  deviceForm.location = "";
  deviceForm.community = "";
  dialogVisible.value = true;
};
const openEditDialog = (device) => {
  dialogMode.value = "edit";
  editingDeviceId.value = device.id;
  deviceForm.id = device.id;
  deviceForm.location = device.location;
  deviceForm.community = device.community;
  dialogVisible.value = true;
};
const handleSaveDevice = async () => {
  if (!deviceForm.id || !deviceForm.location || !deviceForm.community) {
    ElMessage.error("请完整填写设备信息");
    return;
  }
  try {
    if (dialogMode.value === "create") {
      await createDevice({
        id: deviceForm.id,
        name: `新设备 ${deviceForm.id}`,
        status: "online",
        location: deviceForm.location,
        community: deviceForm.community,
      });
      ElMessage.success("新增设备成功");
    } else {
      await updateDevice(editingDeviceId.value, {
        location: deviceForm.location,
        community: deviceForm.community,
      });
      ElMessage.success("设备信息已更新");
    }
    await fetchDevices();
    dialogVisible.value = false;
    currentPage.value = 1;
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "保存设备失败");
  }
};

const handleSearch = () => { fetchDevices({ resetPage: true }); };
const handleReset = () => {
  filters.keyword = "";
  filters.status = "all";
  filters.community = "all";
  fetchDevices({ resetPage: true });
};
const handleRefresh = () => {
  fetchDevices({ resetPage: false });
  fetchOverview();
};

onMounted(() => {
  fetchDevices({ resetPage: true });
  fetchOverview();
  autoRefreshTimer = window.setInterval(() => {
    fetchDevices({ resetPage: false });
    fetchOverview();
  }, 5000);
});

onBeforeUnmount(() => {
  if (autoRefreshTimer) {
    window.clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
  }
});
</script>

<style scoped lang="scss">
.devices-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.overview-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.sum-card {
  padding: 16px 18px;
  border-radius: 18px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.sum-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 209, 255, 0.35) !important;
}

.sum-card.active {
  border-color: rgba(0, 209, 255, 0.6) !important;
  box-shadow: 0 0 0 1px rgba(0, 209, 255, 0.35), 0 0 22px rgba(0, 209, 255, 0.22);
}

.sum-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.s-label {
  color: #94a3b8;
  font-size: 13px;
  letter-spacing: 0.04em;
}

.s-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.tone-cyan .s-dot { background: #00d1ff; box-shadow: 0 0 10px rgba(0,209,255,0.8); }
.tone-success .s-dot { background: #22d3a5; box-shadow: 0 0 10px rgba(34,211,165,0.8); }
.tone-warn .s-dot { background: #f5a524; box-shadow: 0 0 10px rgba(245,165,36,0.8); }
.tone-danger .s-dot { background: #ff5470; box-shadow: 0 0 10px rgba(255,84,112,0.85); }

.s-value {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  font-family: var(--font-family-mono);
  letter-spacing: 0.02em;
  color: #f1f5f9;
}

.tone-cyan .s-value { color: #00d1ff; text-shadow: 0 0 14px rgba(0,209,255,0.45); }
.tone-success .s-value { color: #22d3a5; text-shadow: 0 0 14px rgba(34,211,165,0.45); }
.tone-warn .s-value { color: #f5a524; text-shadow: 0 0 14px rgba(245,165,36,0.45); }
.tone-danger .s-value { color: #ff5470; text-shadow: 0 0 14px rgba(255,84,112,0.45); }

.s-value em {
  font-style: normal;
  font-size: 12px;
  color: #64748b;
  margin-left: 6px;
  text-shadow: none;
  font-family: var(--font-family-base);
  font-weight: 500;
}

.s-sub {
  margin-top: 8px;
  color: #64748b;
  font-size: 12px;
}

.filter-bar {
  padding: 14px 18px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-item.keyword { width: 260px; }
.filter-item.status,
.filter-item.community { width: 150px; }

.iconify-dot {
  color: #00d1ff;
  font-weight: 700;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-toggle {
  display: inline-flex;
  padding: 3px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.view-toggle button {
  padding: 6px 14px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.view-toggle button.active {
  background: rgba(0, 209, 255, 0.12);
  color: #00d1ff;
  box-shadow: inset 0 0 0 1px rgba(0, 209, 255, 0.35);
}

.grid-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 14px;
}

.device-card {
  position: relative;
  padding: 16px 18px;
  border-radius: 18px;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  overflow: hidden;
}

.device-card:hover {
  transform: translateY(-3px);
  border-color: rgba(0, 209, 255, 0.35) !important;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(0, 209, 255, 0.2);
}

.status-bg-triggered { border-color: rgba(255, 84, 112, 0.35) !important; }
.status-bg-offline { border-color: rgba(245, 165, 36, 0.3) !important; }

.device-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.d-id {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.d-id .id {
  color: #00d1ff;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-shadow: 0 0 10px rgba(0, 209, 255, 0.35);
}

.d-id .name {
  color: #f1f5f9;
  font-weight: 600;
  font-size: 15px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid;
}

.status-chip .chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.chip-online {
  color: #7ff3d1;
  border-color: rgba(34, 211, 165, 0.5);
  background: rgba(34, 211, 165, 0.08);
  .chip-dot { background: #22d3a5; box-shadow: 0 0 8px rgba(34,211,165,0.85); animation: pulse-dot 1.8s infinite; }
}

.chip-offline {
  color: #ffd08a;
  border-color: rgba(245, 165, 36, 0.5);
  background: rgba(245, 165, 36, 0.08);
  .chip-dot { background: #f5a524; box-shadow: 0 0 8px rgba(245,165,36,0.85); }
}

.chip-triggered {
  color: #ffb3c1;
  border-color: rgba(255, 84, 112, 0.55);
  background: rgba(255, 84, 112, 0.1);
  .chip-dot { background: #ff5470; box-shadow: 0 0 8px rgba(255,84,112,0.85); animation: pulse-dot 1.2s infinite; }
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.meta span {
  color: #64748b;
  font-size: 11px;
  letter-spacing: 0.06em;
}

.meta strong {
  color: #e2e8f0;
  font-size: 13px;
  font-weight: 500;
}

.gauge-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}

.gauge {
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.gauge-head {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.gauge-head .low {
  color: #ff5470;
  text-shadow: 0 0 10px rgba(255, 84, 112, 0.5);
}

.gauge-bar {
  height: 5px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.gauge-bar span {
  display: block;
  height: 100%;
  border-radius: 3px;
  box-shadow: 0 0 10px rgba(0, 209, 255, 0.35);
  transition: width 0.3s ease;
}

.actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  padding-top: 10px;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
}

.card-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(200px 120px at 100% 0%, rgba(0, 209, 255, 0.12), transparent 70%);
}

.status-bg-triggered .card-glow {
  background: radial-gradient(200px 120px at 100% 0%, rgba(255, 84, 112, 0.16), transparent 70%);
}

.table-list {
  border-radius: 16px;
  padding: 8px 12px;
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

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.4); opacity: 0.6; }
}

@media (max-width: 900px) {
  .overview-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-right {
    justify-content: space-between;
  }
  .meta-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
