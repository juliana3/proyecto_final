// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:4000', // URL base de tu backend Flask
});

export default api;
