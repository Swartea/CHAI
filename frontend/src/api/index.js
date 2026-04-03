import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const healthCheck = () => api.get('/health');

export const getStatus = () => api.get('/status');

export const novelApi = {
  create: (data) => api.post('/novel/create', data),
  list: () => api.get('/novel/list'),
  get: (id) => api.get(`/novel/${id}`),
  delete: (id) => api.delete(`/novel/${id}`),
};

export const worldApi = {
  build: (data) => api.post('/world/build', data),
  get: (novelId) => api.get(`/world/${novelId}`),
  update: (novelId, data) => api.put(`/world/${novelId}`, data),
};

export const chapterApi = {
  write: (data) => api.post('/chapter/write', data),
  list: (novelId) => api.get(`/chapter/list/${novelId}`),
  get: (novelId, index) => api.get(`/chapter/${novelId}/${index}`),
};

export const deconstructApi = {
  run: (data) => api.post('/deconstruct/run', data),
  listTemplates: (genre) => api.get('/deconstruct/templates', { params: { genre } }),
  getTemplate: (id) => api.get(`/deconstruct/templates/${id}`),
};

export default api;
