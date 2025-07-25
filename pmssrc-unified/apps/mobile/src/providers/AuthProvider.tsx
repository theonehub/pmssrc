import React, { createContext, useContext, useEffect, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';
import { apiClient } from '@pmssrc/api-client';
import { User, AuthResponse } from '@pmssrc/shared-types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithBiometric: () => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  isBiometricAvailable: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isBiometricAvailable, setIsBiometricAvailable] = useState(false);

  useEffect(() => {
    initializeAuth();
    checkBiometricAvailability();
  }, []);

  const initializeAuth = async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        apiClient.setToken(token);
        await refreshToken();
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkBiometricAvailability = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      setIsBiometricAvailable(hasHardware && isEnrolled);
    } catch (error) {
      console.error('Failed to check biometric availability:', error);
      setIsBiometricAvailable(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.login({ email, password });
      
      // Store token securely
      await SecureStore.setItemAsync('auth_token', response.access_token);
      await SecureStore.setItemAsync('user_data', JSON.stringify(response.user));
      
      setUser(response.user);
      apiClient.setToken(response.access_token);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithBiometric = async () => {
    try {
      setIsLoading(true);
      
      // Check if biometric is available
      if (!isBiometricAvailable) {
        throw new Error('Biometric authentication not available');
      }

      // Authenticate with biometric
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to access PMSSRC',
        fallbackLabel: 'Use PIN',
        cancelLabel: 'Cancel',
      });

      if (!result.success) {
        throw new Error('Biometric authentication failed');
      }

      // Get stored token and validate
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        throw new Error('No stored authentication token');
      }

      // Validate token with backend
      const response = await apiClient.validateToken(token);
      
      setUser(response.user);
      apiClient.setToken(response.access_token);
    } catch (error) {
      console.error('Biometric login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Call logout endpoint
      await apiClient.logout();
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      // Clear local storage
      await SecureStore.deleteItemAsync('auth_token');
      await SecureStore.deleteItemAsync('user_data');
      
      setUser(null);
      apiClient.setToken(null);
    }
  };

  const refreshToken = async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        setUser(null);
        return;
      }

      const response = await apiClient.validateToken(token);
      setUser(response.user);
      apiClient.setToken(response.access_token);
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Token is invalid, clear it
      await SecureStore.deleteItemAsync('auth_token');
      await SecureStore.deleteItemAsync('user_data');
      setUser(null);
      apiClient.setToken(null);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    loginWithBiometric,
    logout,
    refreshToken,
    isBiometricAvailable,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 