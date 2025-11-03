// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});
console.log("VITE_API_URL:", import.meta.env.VITE_API_URL);
export default api;
