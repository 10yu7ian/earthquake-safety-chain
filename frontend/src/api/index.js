import request from "./request";

export const login = (username, password) =>
  request.post("/login", { username, password }).then((res) => res.data);

export const getDevices = (params = {}) =>
  request.get("/devices", { params }).then((res) => res.data);

export const createDevice = (payload) =>
  request.post("/devices", payload).then((res) => res.data);

export const updateDevice = (deviceId, payload) =>
  request.put(`/devices/${deviceId}`, payload).then((res) => res.data);

export const getEvents = (params = {}) =>
  request.get("/events", { params }).then((res) => res.data);

export const getStatistics = () =>
  request.get("/statistics").then((res) => res.data);

export const sendControl = (device_id, command) =>
  request.post("/control", { device_id, command }).then((res) => res.data);

export const exportEvents = (params = {}) =>
  request.get("/events/export", { params, responseType: "blob" }).then((res) => res.data);
