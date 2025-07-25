import { apiClient } from '@pmssrc/api-client';
import { User } from '@pmssrc/shared-types';
import { NetworkService } from '../../../shared/utils/NetworkService';

export class UserService {
  private networkService: NetworkService;

  constructor() {
    this.networkService = new NetworkService();
  }

  async getCurrentUser(): Promise<User> {
    return this.networkService.withInternetCheck(async () => {
      return await apiClient.getCurrentUser();
    });
  }

  async updateProfile(userData: Partial<User>): Promise<User> {
    return this.networkService.withInternetCheck(async () => {
      return await apiClient.updateUser(userData);
    });
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    return this.networkService.withInternetCheck(async () => {
      await apiClient.changePassword(currentPassword, newPassword);
    });
  }

  async getUsersByOrganisation(organisationId: string): Promise<User[]> {
    return this.networkService.withInternetCheck(async () => {
      return await apiClient.getUsersByOrganisation(organisationId);
    });
  }

  async deleteUser(userId: string): Promise<void> {
    return this.networkService.withInternetCheck(async () => {
      await apiClient.deleteUser(userId);
    });
  }

  // Utility methods
  formatUserName(user: User): string {
    return `${user.first_name} ${user.last_name}`.trim();
  }

  formatUserRole(role: string): string {
    return role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
  }

  isActiveUser(user: User): boolean {
    return user.is_active;
  }

  getMemberSinceDate(user: User): string {
    return new Date(user.created_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}

export const userService = new UserService(); 