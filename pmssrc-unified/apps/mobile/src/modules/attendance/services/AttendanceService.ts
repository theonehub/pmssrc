import { apiClient } from '@pmssrc/api-client';
import { AttendanceCreateRequest, AttendanceRecord, LocationData } from '@pmssrc/shared-types';
import { NetworkService } from '../../../shared/utils/NetworkService';

export class AttendanceService {
  private networkService: NetworkService;

  constructor() {
    this.networkService = new NetworkService();
  }

  async checkIn(locationData: LocationData): Promise<AttendanceRecord> {
    return this.networkService.withInternetCheck(async () => {
      const request: AttendanceCreateRequest = {
        check_in_time: new Date().toISOString(),
        location: locationData,
        status: 'PRESENT'
      };
      
      return await apiClient.createAttendance(request);
    });
  }

  async checkOut(locationData: LocationData): Promise<AttendanceRecord> {
    return this.networkService.withInternetCheck(async () => {
      const request: AttendanceCreateRequest = {
        check_out_time: new Date().toISOString(),
        location: locationData,
        status: 'PRESENT'
      };
      
      return await apiClient.createAttendance(request);
    });
  }

  async getTodayAttendance(): Promise<AttendanceRecord | null> {
    return this.networkService.withInternetCheck(async () => {
      const today = new Date().toISOString().split('T')[0];
      const attendance = await apiClient.getAttendanceByDate(today);
      return attendance.length > 0 ? attendance[0] : null;
    });
  }

  async getAttendanceHistory(startDate: string, endDate: string): Promise<AttendanceRecord[]> {
    return this.networkService.withInternetCheck(async () => {
      return await apiClient.getAttendanceByDateRange(startDate, endDate);
    });
  }

  async getAttendanceAnalytics(month: string, year: string): Promise<any> {
    return this.networkService.withInternetCheck(async () => {
      return await apiClient.getAttendanceAnalytics(month, year);
    });
  }

  // Utility methods
  isCheckedInToday(attendance: AttendanceRecord | null): boolean {
    if (!attendance) return false;
    return !!attendance.check_in_time && !attendance.check_out_time;
  }

  isCheckedOutToday(attendance: AttendanceRecord | null): boolean {
    if (!attendance) return false;
    return !!attendance.check_in_time && !!attendance.check_out_time;
  }

  getWorkingHours(attendance: AttendanceRecord): number {
    if (!attendance.check_in_time || !attendance.check_out_time) return 0;
    
    const checkIn = new Date(attendance.check_in_time);
    const checkOut = new Date(attendance.check_out_time);
    const diffMs = checkOut.getTime() - checkIn.getTime();
    return Math.round((diffMs / (1000 * 60 * 60)) * 100) / 100; // Hours with 2 decimal places
  }

  formatTime(timeString: string): string {
    return new Date(timeString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  }

  getAttendanceStatus(attendance: AttendanceRecord | null): 'NOT_CHECKED_IN' | 'CHECKED_IN' | 'CHECKED_OUT' {
    if (!attendance) return 'NOT_CHECKED_IN';
    if (!attendance.check_in_time) return 'NOT_CHECKED_IN';
    if (!attendance.check_out_time) return 'CHECKED_IN';
    return 'CHECKED_OUT';
  }
}

export const attendanceService = new AttendanceService(); 