// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.production.VITE_API_URL || 'http://localhost:4000',
});

export default api;
