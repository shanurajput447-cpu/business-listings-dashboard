import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getCityCounts = async () => {
  const response = await apiClient.get("/api/dashboard/city");
  return response.data;
};

export const getCategoryCounts = async () => {
  const response = await apiClient.get("/api/dashboard/category");
  return response.data;
};

export const getSourceCounts = async () => {
  const response = await apiClient.get("/api/dashboard/source");
  return response.data;
};

export default apiClient;
