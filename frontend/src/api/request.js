import axios from "axios";
import { isDemoMode } from "./demo";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
});

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

request.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401 && !isDemoMode()) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default request;
