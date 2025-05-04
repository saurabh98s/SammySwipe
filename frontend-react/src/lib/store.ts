import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { auth, users } from './api';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  gender: string;
  birth_date: string;
  bio?: string;
  interests: string[];
  location?: string;
  profile_photo?: string;
  match_score?: number;
}

// Extended interface with superuser capabilities
interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isSuperUser: boolean;
  enableSuperUser: () => void;
  disableSuperUser: () => void;
  login: (email: string, password: string) => Promise<void>;
  loginAsSuperUser: () => void;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isLoading: false,
      error: null,
      isSuperUser: false,
      
      // New superuser functions
      enableSuperUser: () => {
        set({ isSuperUser: true });
      },
      
      disableSuperUser: () => {
        set({ isSuperUser: false });
      },
      
      loginAsSuperUser: () => {
        // Create a mock superuser with all access
        const superUser: User = {
          id: 'super-admin',
          email: 'superuser@sammyswipe.com',
          username: 'superadmin',
          full_name: 'Super Admin',
          gender: 'other',
          birth_date: new Date().toISOString(),
          bio: 'System administrator with full access',
          interests: ['system administration', 'security'],
          location: 'System',
          profile_photo: '/images/admin.png',
        };
        set({ 
          user: superUser, 
          isSuperUser: true,
          token: 'super-admin-token'
        });
      },
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const data = await auth.login(email, password);
          localStorage.setItem('token', data.access_token);
          set({ token: data.access_token });
          await get().fetchUser();
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Login failed' });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },
      
      register: async (userData: any) => {
        set({ isLoading: true, error: null });
        try {
          await auth.register(userData);
          // After registration, redirect to login
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Registration failed' });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },
      
      logout: () => {
        localStorage.removeItem('token');
        set({ token: null, user: null, isSuperUser: false });
      },
      
      fetchUser: async () => {
        const { token, isSuperUser } = get();
        if (!token || isSuperUser) return;
        
        set({ isLoading: true, error: null });
        try {
          const user = await users.getCurrentUser();
          set({ user });
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Failed to fetch user data' });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token,
        isSuperUser: state.isSuperUser
      }),
    }
  )
); 