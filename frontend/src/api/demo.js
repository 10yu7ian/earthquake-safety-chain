const now = new Date();
const hoursAgo = (h) => new Date(now.getTime() - h * 3600 * 1000).toISOString();
const minutesAgo = (m) => new Date(now.getTime() - m * 60 * 1000).toISOString();

const initialDevices = [
  {
    id: "LM-1001",
    name: "东门节点A1",
    location: "东门围栏北侧",
    community: "龙门一社区",
    status: "online",
    last_seen: minutesAgo(2),
    created_at: hoursAgo(72),
  },
  {
    id: "LM-1002",
    name: "东门节点A2",
    location: "东门围栏南侧",
    community: "龙门一社区",
    status: "online",
    last_seen: minutesAgo(5),
    created_at: hoursAgo(72),
  },
  {
    id: "LM-1003",
    name: "西门监测点",
    location: "西门停车场",
    community: "龙门二社区",
    status: "triggered",
    last_seen: minutesAgo(18),
    created_at: hoursAgo(72),
  },
  {
    id: "LM-1004",
    name: "北门阀井",
    location: "北门桥下",
    community: "龙门二社区",
    status: "online",
    last_seen: minutesAgo(8),
    created_at: hoursAgo(72),
  },
  {
    id: "LM-1005",
    name: "中心站",
    location: "物业大楼东侧",
    community: "龙门一社区",
    status: "online",
    last_seen: minutesAgo(1),
    created_at: hoursAgo(72),
  },
];

const initialEvents = [
  {
    id: 1,
    device_id: "LM-1003",
    event_type: "shutdown",
    acc_max: 3.82,
    details: "timestamp=" + minutesAgo(18),
    created_at: minutesAgo(18),
  },
  {
    id: 2,
    device_id: "LM-1001",
    event_type: "check",
    acc_max: 0.42,
    details: "timestamp=" + minutesAgo(45),
    created_at: minutesAgo(45),
  },
  {
    id: 3,
    device_id: "LM-1002",
    event_type: "restore",
    acc_max: 0.15,
    details: "timestamp=" + hoursAgo(2),
    created_at: hoursAgo(2),
  },
  {
    id: 4,
    device_id: "LM-1004",
    event_type: "check",
    acc_max: 0.28,
    details: "timestamp=" + hoursAgo(3),
    created_at: hoursAgo(3),
  },
  {
    id: 5,
    device_id: "LM-1005",
    event_type: "shutdown",
    acc_max: 2.95,
    details: "timestamp=" + hoursAgo(5),
    created_at: hoursAgo(5),
  },
  {
    id: 6,
    device_id: "LM-1005",
    event_type: "restore",
    acc_max: 0.08,
    details: "timestamp=" + hoursAgo(4),
    created_at: hoursAgo(4),
  },
  {
    id: 7,
    device_id: "LM-1001",
    event_type: "check",
    acc_max: 0.35,
    details: "timestamp=" + hoursAgo(6),
    created_at: hoursAgo(6),
  },
  {
    id: 8,
    device_id: "LM-1003",
    event_type: "shutdown",
    acc_max: 4.12,
    details: "timestamp=" + hoursAgo(8),
    created_at: hoursAgo(8),
  },
];

let devices = initialDevices.map((item) => ({ ...item }));
let events = initialEvents.map((item) => ({ ...item }));
let nextEventId = events.length + 1;

export const isDemoMode = () => import.meta.env.VITE_DEMO_MODE === "true";

const delay = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));

const todayStart = () => {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
};

const buildStatistics = () => {
  const start = todayStart();
  const todayEvents = events.filter((ev) => new Date(ev.created_at) >= start);
  return {
    total_devices: devices.length,
    online_devices: devices.filter((d) => d.status === "online").length,
    today_events: todayEvents.length,
    today_triggers: todayEvents.filter((ev) => ev.event_type === "shutdown").length,
    alert_count: devices.filter((d) => d.status === "triggered").length,
  };
};

const filterDevices = (params = {}) => {
  let list = [...devices];
  if (params.status) {
    list = list.filter((d) => d.status === params.status);
  }
  if (params.community) {
    list = list.filter((d) => d.community === params.community);
  }
  const limit = Number(params.limit) || list.length;
  return list.slice(0, limit);
};

const filterEvents = (params = {}) => {
  let list = [...events].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
  if (params.device_id) {
    list = list.filter((ev) => ev.device_id === params.device_id);
  }
  if (params.event_type) {
    list = list.filter((ev) => ev.event_type === params.event_type);
  }
  const limit = Number(params.limit) || list.length;
  return list.slice(0, limit);
};

export const demoLogin = async (username, password) => {
  await delay();
  if (username === "admin" && password === "admin123") {
    return { access_token: "demo-token-admin", token_type: "bearer" };
  }
  if (username === "user" && password === "user123") {
    return { access_token: "demo-token-user", token_type: "bearer" };
  }
  const error = new Error("Invalid username or password");
  error.response = { status: 401, data: { detail: "Invalid username or password" } };
  throw error;
};

export const demoGetDevices = async (params = {}) => {
  await delay();
  return filterDevices(params);
};

export const demoCreateDevice = async (payload) => {
  await delay();
  if (devices.some((d) => d.id === payload.id)) {
    const error = new Error("Device already exists");
    error.response = { status: 400, data: { detail: "Device already exists" } };
    throw error;
  }
  const device = {
    id: payload.id,
    name: payload.name || payload.id,
    location: payload.location || null,
    community: payload.community || null,
    status: payload.status || "online",
    last_seen: new Date().toISOString(),
    created_at: new Date().toISOString(),
  };
  devices.push(device);
  return device;
};

export const demoUpdateDevice = async (deviceId, payload) => {
  await delay();
  const index = devices.findIndex((d) => d.id === deviceId);
  if (index < 0) {
    const error = new Error("Device not found");
    error.response = { status: 404, data: { detail: "Device not found" } };
    throw error;
  }
  devices[index] = {
    ...devices[index],
    ...payload,
    last_seen: new Date().toISOString(),
  };
  return devices[index];
};

export const demoGetEvents = async (params = {}) => {
  await delay();
  return filterEvents(params);
};

export const demoGetStatistics = async () => {
  await delay();
  return buildStatistics();
};

export const demoSendControl = async (device_id, command) => {
  await delay(300);
  const device = devices.find((d) => d.id === device_id);
  if (!device) {
    const error = new Error("Device not found");
    error.response = { status: 404, data: { detail: "Device not found" } };
    throw error;
  }
  if (command === "reset" || command === "restore") {
    device.status = "online";
    events.unshift({
      id: nextEventId++,
      device_id,
      event_type: "restore",
      acc_max: 0,
      details: `command=${command}`,
      created_at: new Date().toISOString(),
    });
  } else if (command === "self_check") {
    events.unshift({
      id: nextEventId++,
      device_id,
      event_type: "check",
      acc_max: Number((Math.random() * 0.8 + 0.1).toFixed(2)),
      details: "command=self_check",
      created_at: new Date().toISOString(),
    });
  }
  return { status: "ok", command };
};

export const demoExportEvents = async (params = {}) => {
  await delay();
  const rows = filterEvents(params);
  const header = "id,device_id,event_type,acc_max,details,created_at\n";
  const body = rows
    .map((ev) =>
      [ev.id, ev.device_id, ev.event_type, ev.acc_max ?? "", ev.details ?? "", ev.created_at]
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(",")
    )
    .join("\n");
  return new Blob([header + body], { type: "text/csv;charset=utf-8;" });
};
