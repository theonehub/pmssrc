import { BaseAPI } from './baseApi';

/**
 * Export API service for file generation
 * Handles all export operations through backend APIs
 */
class ExportAPI {
  private static instance: ExportAPI;
  private baseApi: BaseAPI;

  private constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  public static getInstance(): ExportAPI {
    if (!ExportAPI.instance) {
      ExportAPI.instance = new ExportAPI();
    }
    return ExportAPI.instance;
  }

  /**
   * Export processed salaries in specified format
   */
  async exportProcessedSalaries(
    formatType: 'csv' | 'excel' | 'bank_transfer',
    month: number,
    year: number,
    filters?: {
      status?: string;
      department?: string;
    }
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams({
        month: month.toString(),
        year: year.toString(),
        ...(filters?.status && { status: filters.status }),
        ...(filters?.department && { department: filters.department })
      });

      const response = await this.baseApi.download(
        `/api/v2/exports/processed-salaries/${formatType}?${params.toString()}`
      );
      return response;
    } catch (error: any) {
      console.error('Error exporting processed salaries:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export processed salaries');
    }
  }

  /**
   * Export TDS report in specified format
   */
  async exportTDSReport(
    formatType: 'csv' | 'excel' | 'form_16' | 'form_24q' | 'fvu',
    month: number,
    year: number,
    quarter?: number,
    filters?: {
      status?: string;
      department?: string;
    }
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams({
        month: month.toString(),
        year: year.toString(),
        ...(filters?.status && { status: filters.status }),
        ...(filters?.department && { department: filters.department }),
        ...(quarter && { quarter: quarter.toString() })
      });

      const response = await this.baseApi.download(
        `/api/v2/exports/tds-report/${formatType}?${params.toString()}`
      );
      return response;
    } catch (error: any) {
      console.error('Error exporting TDS report:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export TDS report');
    }
  }

  /**
   * Export Form 16 for specific employee
   */
  async exportForm16(
    employeeId: string,
    taxYear?: string
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams();
      if (taxYear) {
        params.append('tax_year', taxYear);
      }

      const response = await this.baseApi.download(
        `/api/v2/exports/form-16/${employeeId}?${params.toString()}`
      );
      return response;
    } catch (error: any) {
      console.error('Error exporting Form 16:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export Form 16');
    }
  }

  /**
   * Export Form 24Q for specific quarter and year
   */
  async exportForm24Q(
    quarter: number,
    year: number,
    formatType: 'csv' | 'fvu' = 'csv'
  ): Promise<Blob> {
    try {
      const response = await this.baseApi.download(
        `/api/v2/exports/form-24q/quarter/${quarter}/year/${year}?format_type=${formatType}`
      );
      return response;
    } catch (error: any) {
      console.error('Error exporting Form 24Q:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export Form 24Q');
    }
  }

  /**
   * Export PF report in specified format
   */
  async exportPFReport(
    formatType: 'csv' | 'excel' | 'challan' | 'return',
    month: number,
    year: number,
    quarter?: number,
    filters?: {
      status?: string;
      department?: string;
    }
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams({
        month: month.toString(),
        year: year.toString(),
        ...(filters?.status && { status: filters.status }),
        ...(filters?.department && { department: filters.department }),
        ...(quarter && { quarter: quarter.toString() })
      });

      const response = await this.baseApi.download(
        `/api/v2/exports/pf-report/${formatType}?${params.toString()}`
      );
      return response;
    } catch (error: any) {
      console.error('Error exporting PF report:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export PF report');
    }
  }

  /**
   * Download file with proper filename
   */
  downloadFile(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

// Export singleton instance
export const exportApi = ExportAPI.getInstance();
export default exportApi; 