import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService from '../shared/api/authService';
import { User } from '../shared/types';

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (credentials: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check if user is authenticated using authService
    const token = authService.isAuthenticated();
    const userData = authService.getCurrentUser();
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(userData);
    }
  }, []);

  const login = async (credentials: any) => {
    try {
      // Call authService.login which handles the login API call
      await authService.login(credentials);
      
      // After successful login, refresh user data to get complete profile
      const userData = await authService.refreshUserData();
      
      if (userData) {
        setIsAuthenticated(true);
        setUser(userData);
      } else {
        // Fallback to stored user data if refresh fails
        const storedUser = authService.getCurrentUser();
        if (storedUser) {
          setIsAuthenticated(true);
          setUser(storedUser);
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 