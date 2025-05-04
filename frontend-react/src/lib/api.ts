import axios from 'axios';
import { useAuthStore } from './store';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const RANDOM_USER_API = 'https://randomuser.me/api/';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to fetch random users from the RandomUser API
async function fetchRandomUsers(count = 10) {
  try {
    const response = await axios.get(`${RANDOM_USER_API}?results=${count}&nat=us,gb,ca,au,fr,de`);
    return response.data.results;
  } catch (error) {
    console.error('Error fetching random users:', error);
    return [];
  }
}

// Helper function to transform RandomUser API data to our app format
function transformRandomUserToAppFormat(user) {
  const interests = [
    "Travel", "Photography", "Cooking", "Fitness", "Reading", 
    "Art", "Music", "Movies", "Gaming", "Technology", 
    "Fashion", "Hiking", "Yoga", "Dancing", "Writing"
  ];
  
  // Get 2-5 random interests
  const userInterests = [];
  const numInterests = Math.floor(Math.random() * 4) + 2; // 2-5 interests
  const interestsCopy = [...interests];
  
  for (let i = 0; i < numInterests; i++) {
    if (interestsCopy.length === 0) break;
    const randomIndex = Math.floor(Math.random() * interestsCopy.length);
    userInterests.push(interestsCopy[randomIndex]);
    interestsCopy.splice(randomIndex, 1);
  }
  
  // Get 0-3 common topics (subset of interests)
  const commonTopics = [];
  const numCommonTopics = Math.floor(Math.random() * 4); // 0-3 common topics
  const interestsForCommon = [...userInterests];
  
  for (let i = 0; i < numCommonTopics; i++) {
    if (interestsForCommon.length === 0) break;
    const randomIndex = Math.floor(Math.random() * interestsForCommon.length);
    commonTopics.push(interestsForCommon[randomIndex]);
    interestsForCommon.splice(randomIndex, 1);
  }
  
  return {
    id: user.login.uuid,
    email: user.email,
    username: user.login.username,
    full_name: `${user.name.first} ${user.name.last}`,
    gender: user.gender,
    birth_date: user.dob.date,
    bio: `Hi, I'm ${user.name.first}! I'm from ${user.location.city} and enjoy ${userInterests.slice(0, 2).join(' and ')}.`,
    interests: userInterests,
    location: `${user.location.city}, ${user.location.country}`,
    profile_photo: user.picture.large,
    match_score: Math.random() * 0.5 + 0.4, // Match score between 0.4 and 0.9
    common_topics: commonTopics
  };
}

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
  async (error) => {
    // Get superuser state from localStorage to avoid circular dependency
    const authState = JSON.parse(localStorage.getItem('auth-storage') || '{}');
    const isSuperUser = authState?.state?.isSuperUser;
    
    // If in superuser mode, create a realistic mock response
    if (isSuperUser && error.response?.status === 401) {
      console.log('Super user mode: Bypassing authentication for', error.config.url);
      
      // Create a mock response based on the request URL
      let mockData = {};
      
      // Handle different API endpoints with appropriate mock data
      if (error.config.url.includes('/users/me')) {
        // Fetch a single random user for current user profile
        const users = await fetchRandomUsers(1);
        if (users.length > 0) {
          mockData = transformRandomUserToAppFormat(users[0]);
          mockData.full_name = 'Super Admin';
          mockData.email = 'superuser@sammyswipe.com';
          mockData.bio = 'System administrator with full access to all features';
        }
      } else if (error.config.url.includes('/matches/recommendations')) {
        // Fetch multiple random users for recommendations
        const users = await fetchRandomUsers(10);
        mockData = users.map(transformRandomUserToAppFormat);
      } else if (error.config.url.includes('/matches/my-matches')) {
        // Fetch random users for matches
        const users = await fetchRandomUsers(5);
        mockData = users.map(user => {
          const transformedUser = transformRandomUserToAppFormat(user);
          return {
            id: transformedUser.id,
            full_name: transformedUser.full_name,
            bio: transformedUser.bio,
            profile_photo: transformedUser.profile_photo,
            last_message: ['Hey there!', 'How are you?', 'Nice to meet you!'][Math.floor(Math.random() * 3)],
            timestamp: new Date().toISOString()
          };
        });
      } else if (error.config.url.includes('/chat')) {
        // Mock chat messages
        mockData = Array(10).fill(0).map((_, i) => ({
          id: `msg-${i}`,
          sender_id: i % 2 === 0 ? 'super-admin' : 'user-1',
          content: [
            "Hey there! How are you doing?",
            "I'm good, thanks for asking! How about you?",
            "I've been great! Just busy with work lately.",
            "Same here. We should catch up sometime.",
            "Definitely! Are you free this weekend?",
            "Yeah, I should be. What did you have in mind?",
            "Maybe we could grab coffee or lunch?",
            "That sounds perfect. How about Saturday afternoon?",
            "Works for me! Looking forward to it.",
            "Me too! See you then!"
          ][i],
          timestamp: new Date(Date.now() - (10 - i) * 3600000).toISOString(),
        }));
      }
      
      // Return a resolved promise with realistic mock data
      return Promise.resolve({
        data: mockData,
        status: 200,
        statusText: 'OK (Super Admin Mode)',
        headers: {},
        config: error.config,
      });
    }
    
    // Normal error handling for non-superuser or other errors
    if (error.response?.status === 401) {
      // Handle unauthorized access (e.g., redirect to login)
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth service
export const auth = {
  login: async (email: string, password: string) => {
    const authState = JSON.parse(localStorage.getItem('auth-storage') || '{}');
    const isSuperUser = authState?.state?.isSuperUser;
    
    // If superuser mode is enabled, return mock token
    if (isSuperUser) {
      return { access_token: 'super-admin-token' };
    }
    
    const response = await api.post('/auth/token', new URLSearchParams({
      username: email,
      password,
    }));
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