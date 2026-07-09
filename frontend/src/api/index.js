import request from "./request";
import {
  demoCreateDevice,
  demoExportEvents,
  demoGetDevices,
  demoGetEvents,
  demoGetStatistics,
  demoLogin,
  demoSendControl,
  demoUpdateDevice,
  isDemoMode,
} from "./demo";

export const login = (username, password) =>
  isDemoMode()
    ? demoLogin(username, password)
    : request.post("/login", { username, password }).then((res) => res.data);

export const getDevices = (params = {}) =>
  isDemoMode()
    ? demoGetDevices(params)
    : request.get("/devices", { params }).then((res) => res.data);

export const createDevice = (payload) =>
  isDemoMode()
    ? demoCreateDevice(payload)
    : request.post("/devices", payload).then((res) => res.data);

export const updateDevice = (deviceId, payload) =>
  isDemoMode()
    ? demoUpdateDevice(deviceId, payload)
    : request.put(`/devices/${deviceId}`, payload).then((res) => res.data);

export const getEvents = (params = {}) =>
  isDemoMode()
    ? demoGetEvents(params)
    : request.get("/events", { params }).then((res) => res.data);

export const getStatistics = () =>
  isDemoMode()
    ? demoGetStatistics()
    : request.get("/statistics").then((res) => res.data);

export const sendControl = (device_id, command) =>
  isDemoMode()
    ? demoSendControl(device_id, command)
    : request.post("/control", { device_id, command }).then((res) => res.data);

export const exportEvents = (params = {}) =>
  isDemoMode()
    ? demoExportEvents(params)
    : request.get("/events/export", { params, responseType: "blob" }).then((res) => res.data);
