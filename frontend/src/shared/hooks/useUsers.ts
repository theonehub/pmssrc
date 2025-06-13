import { useQuery } from '@tanstack/react-query';
import { UserAPI } from '../api';

export const useUsersQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: async () => {
      const response = await UserAPI.getUsers(filters);
      // Handle both possible response formats
      return response.users || [];
    },
  });
};

export const useUserDetailQuery = (userId: string) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await UserAPI.getUserById(userId);
      return response;
    },
    enabled: !!userId,
  });
};

export const useCreateUserMutation = () => {
  return useQuery({
    queryKey: ['createUser'],
    queryFn: async () => {
      const response = await UserAPI.getUsers();
      // Handle both possible response formats
      return response.users || [];
    },
  });
};

export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await UserAPI.getUsers();
      return response.users || [];
    },
  });
};

export const useUser = (userId: string) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await UserAPI.getUserById(userId);
      return response;
    },
    enabled: !!userId,
  });
}; 