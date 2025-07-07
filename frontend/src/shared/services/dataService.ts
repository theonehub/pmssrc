import { userApi } from '../api/userApi';


// Backward compatibility service for data operations
class DataService {
  // User management methods
  async getAllUsers(filters: any = {}) {
    try {
      return await userApi.getUsers(filters);
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  async getUsers(params?: { skip?: number; limit?: number; search?: string }) {
    try {
      return await userApi.getUsers(params);
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  async getUserById(userId: string) {
    try {
      return await userApi.getUserById(userId);
    } catch (error) {
      console.error('Error fetching user:', error);
      throw error;
    }
  }

  async getUserByEmpIdLegacy(empId: string) {
    try {
      return await userApi.getUserByEmpIdLegacy(empId);
    } catch (error) {
      console.error('Error fetching user by emp ID:', error);
      throw error;
    }
  }

  async createUser(userData: any) {
    try {
      return await userApi.createUser(userData);
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  }

  async createUserWithFiles(userData: any, files?: FileList) {
    try {
      // Convert FileList to UserFiles format if provided
      if (files) {
        const userFiles = {
          documents: files
        };
        return await userApi.createUserWithFiles(userData, userFiles as any);
      } else {
        return await userApi.createUser(userData);
      }
    } catch (error) {
      console.error('Error creating user with files:', error);
      throw error;
    }
  }

  async updateUser(userId: string, userData: any) {
    try {
      return await userApi.updateUser(userId, userData);
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  }

  async updateUserLegacy(empId: string, userData: any) {
    try {
      return await userApi.updateUserLegacy(empId, userData);
    } catch (error) {
      console.error('Error updating user (legacy):', error);
      throw error;
    }
  }

  async deleteUser(userId: string) {
    try {
      return await userApi.deleteUser(userId);
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  }

  async getUserStats() {
    try {
      return await userApi.getUserStats();
    } catch (error) {
      console.error('Error fetching user stats:', error);
      throw error;
    }
  }

  async getDepartments() {
    try {
      return await userApi.getUserDepartments();
    } catch (error) {
      console.error('Error fetching departments:', error);
      throw error;
    }
  }

  async getDesignations() {
    try {
      return await userApi.getUserDesignations();
    } catch (error) {
      console.error('Error fetching designations:', error);
      throw error;
    }
  }

  // Add other data service methods as needed
  async searchUsers(query: string, filters: any = {}) {
    try {
      return await userApi.searchUsers(query, filters);
    } catch (error) {
      console.error('Error searching users:', error);
      throw error;
    }
  }

  async importUsers(file: File) {
    try {
      return await userApi.importUsers(file);
    } catch (error) {
      console.error('Error importing users:', error);
      throw error;
    }
  }

  async downloadUserTemplate(): Promise<Blob> {
    try {
      return await userApi.downloadUserTemplate('csv');
    } catch (error) {
      console.error('Error downloading user template:', error);
      throw error;
    }
  }

  // Payout related methods (mock implementations for now)
  async getMonthlyPayouts(params?: any) {
    try {
      // This would need to be implemented with actual payout API
      console.log('Getting monthly payouts:', params);
      return { data: [], total: 0 };
    } catch (error) {
      console.error('Error fetching monthly payouts:', error);
      throw error;
    }
  }

  async emailPayslip(payoutId: string) {
    try {
      // This would need to be implemented with actual payout API
      console.log('Emailing payslip:', payoutId);
      return { success: true };
    } catch (error) {
      console.error('Error emailing payslip:', error);
      throw error;
    }
  }

  async bulkGeneratePayslips(payoutIds: string[]) {
    try {
      // This would need to be implemented with actual payout API
      console.log('Bulk generating payslips:', payoutIds);
      return { success: true };
    } catch (error) {
      console.error('Error bulk generating payslips:', error);
      throw error;
    }
  }

  async bulkEmailPayslips(payoutIds: string[]) {
    try {
      // This would need to be implemented with actual payout API
      console.log('Bulk emailing payslips:', payoutIds);
      return { success: true };
    } catch (error) {
      console.error('Error bulk emailing payslips:', error);
      throw error;
    }
  }
}

const dataService = new DataService();
export default dataService; 