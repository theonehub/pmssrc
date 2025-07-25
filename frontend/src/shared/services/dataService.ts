import { userApi } from '../api/userApi';


// Backward compatibility service for data operations
class DataService {
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
      return await userApi.getUserById(empId);
    } catch (error) {
      console.error('Error fetching user by emp ID:', error);
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

  async createUserWithFiles(userData: any, files?: { pan_file?: File; aadhar_file?: File; photo?: File }) {
    try {
      // Build UserFiles object with correct field names for backend
      const userFiles: any = {};
      if (files?.pan_file) userFiles.pan_file = files.pan_file;
      if (files?.aadhar_file) userFiles.aadhar_file = files.aadhar_file;
      if (files?.photo) userFiles.photo = files.photo;
      return await userApi.createUserWithFiles(userData, userFiles);
    } catch (error) {
      console.error('Error creating user with files:', error);
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
      return await userApi.downloadTemplate();
    } catch (error) {
      console.error('Error downloading user template:', error);
      throw error;
    }
  }
}

const dataService = new DataService();
export default dataService; 