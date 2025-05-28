import { useMemo } from 'react';
import { getToken, getUserRole } from '../utils/auth';
import { UserRole } from '../types';

interface AuthUser {
  role: UserRole;
}

interface UseAuthReturn {
  token: string | null;
  user: AuthUser | null;
}

export const useAuth = (): UseAuthReturn => {
  const token = getToken();
  const role = getUserRole();

  const user = useMemo((): AuthUser | null => {
    if (token && role) {
      return { role };
    }
    return null;
  }, [token, role]);

  return { token, user };
};
