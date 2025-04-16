import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access (e.g., redirect to login)
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  register: async (userData: any) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  registerTest: async (userData: any) => {
    const response = await api.post('/auth/register_test', userData);
    return response.data;
  },
};

export const users = {
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
  
  updateProfile: async (userData: any) => {
    const response = await api.put('/users/me', userData);
    return response.data;
  },
  
  updatePreferences: async (preferences: any) => {
    const response = await api.put('/users/me/preferences', preferences);
    return response.data;
  },
  
  uploadPhoto: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/users/me/photo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const matches = {
  getRecommendations: async () => {
    const response = await api.get('/matches/recommendations');
    return response.data;
  },
  
  getMyMatches: async () => {
    const response = await api.get('/matches/my-matches');
    return response.data;
  },
  
  like: async (userId: string) => {
    const response = await api.post(`/matches/${userId}`);
    return response.data;
  },
  
  reject: async (userId: string) => {
    const response = await api.put(`/matches/${userId}/reject`);
    return response.data;
  },
};

export const chat = {
  getHistory: async (userId: string) => {
    const response = await api.get(`/chat/${userId}/history`);
    return response.data;
  },
  
  sendMessage: async (userId: string, content: string) => {
    const response = await api.post(`/chat/${userId}`, { content });
    return response.data;
  },
};

export default api; 