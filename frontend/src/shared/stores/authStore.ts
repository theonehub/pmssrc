import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { authApi, type User, type LoginCredentials } from '../api/authApi';

// Platform-agnostic storage
const getStorage = () => {
  if (typeof window !== 'undefined') {
    return localStorage;
  }
  // TODO: Add React Native AsyncStorage support
  return {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
  };
};

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  
  // Utility methods
  hasPermission: (permission: string) => boolean;
  hasRole: (roles: string[]) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      permissions: [],
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginCredentials) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await authApi.login(credentials);
          const { access_token, user_info, permissions } = response;
          
          set({
            user: user_info,
            token: access_token,
            permissions: permissions || [],
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            user: null,
            token: null,
            permissions: [],
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Login failed'
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          set({ isLoading: true });
          
          await authApi.logout();
          
          set({
            user: null,
            token: null,
            permissions: [],
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          // Even if logout fails on server, clear local state
          set({
            user: null,
            token: null,
            permissions: [],
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      refreshUser: async () => {
        try {
          set({ isLoading: true, error: null });
          
          const user = await authApi.getCurrentUserProfile();
          
          set({
            user,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Failed to refresh user data'
          });
          throw error;
        }
      },

      changePassword: async (currentPassword: string, newPassword: string) => {
        try {
          set({ isLoading: true, error: null });
          
          await authApi.changePassword({
            current_password: currentPassword,
            new_password: newPassword
          });
          
          set({
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Failed to change password'
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      // Utility methods
      hasPermission: (permission: string) => {
        const { permissions } = get();
        return permissions.includes(permission);
      },

      hasRole: (roles: string[]) => {
        const { user } = get();
        return user ? roles.includes(user.role) : false;
      },

      hasAnyRole: (roles: string[]) => {
        const { user } = get();
        return user ? roles.some(role => user.role === role) : false;
      }
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => getStorage()),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        permissions: state.permissions,
        isAuthenticated: state.isAuthenticated
      }),
      onRehydrateStorage: () => (state) => {
        // Validate token on rehydration
        if (state?.token && state?.isAuthenticated) {
          authApi.validateToken().catch(() => {
            // If token is invalid, clear auth state
            state.user = null;
            state.token = null;
            state.permissions = [];
            state.isAuthenticated = false;
          });
        }
      }
    }
  )
);

// Selectors for better performance
export const useAuth = () => useAuthStore((state) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  isLoading: state.isLoading,
  error: state.error
}));

export const useAuthActions = () => useAuthStore((state) => ({
  login: state.login,
  logout: state.logout,
  refreshUser: state.refreshUser,
  changePassword: state.changePassword,
  clearError: state.clearError,
  setLoading: state.setLoading
}));

export const usePermissions = () => useAuthStore((state) => ({
  permissions: state.permissions,
  hasPermission: state.hasPermission,
  hasRole: state.hasRole,
  hasAnyRole: state.hasAnyRole
}));

// Legacy compatibility hook (to ease migration from Context)
export const useAuthContext = () => {
  const auth = useAuth();
  const actions = useAuthActions();
  const permissions = usePermissions();
  
  return {
    ...auth,
    ...actions,
    ...permissions,
    // Legacy property names
    currentUser: auth.user,
    loading: auth.isLoading
  };
}; 