import { useMemo } from 'react';
import { 
  getToken, 
  getUserRole, 
  getUserId, 
  getUsername, 
  getHostname, 
  getUserPermissions,
  isAuthenticated,
  hasRole,
  hasPermission,
  hasAnyRole,
  hasAnyPermission,
  hasAllPermissions,
  getTokenExpiration,
  willExpireSoon,
  getAuthContext
} from '../utils/auth';
import { UserRole } from '../types';

interface AuthUser {
  employee_id: string;
  username: string;
  role: UserRole;
  hostname: string;
  permissions: string[];
}

interface UseAuthReturn {
  // Basic auth state
  isAuthenticated: boolean;
  token: string | null;
  user: AuthUser | null;
  
  // Token information
  tokenExpiration: Date | null;
  willExpireSoon: boolean;
  
  // Utility functions
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  
  // Complete context
  authContext: ReturnType<typeof getAuthContext>;
}

export const useAuth = (): UseAuthReturn => {
  const token = getToken();
  const authenticated = isAuthenticated();
  const role = getUserRole();
  const userId = getUserId();
  const username = getUsername();
  const hostname = getHostname();
  const permissions = getUserPermissions();
  const tokenExpiration = getTokenExpiration();
  const willTokenExpireSoon = willExpireSoon();
  const authContext = getAuthContext();

  const user = useMemo((): AuthUser | null => {
    if (authenticated && token && role && userId && username && hostname) {
      return { 
        employee_id: userId,
        username,
        role,
        hostname,
        permissions
      };
    }
    return null;
  }, [authenticated, token, role, userId, username, hostname, permissions]);

  return {
    // Basic auth state
    isAuthenticated: authenticated,
    token,
    user,
    
    // Token information
    tokenExpiration,
    willExpireSoon: willTokenExpireSoon,
    
    // Utility functions
    hasRole,
    hasAnyRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    
    // Complete context
    authContext
  };
};
