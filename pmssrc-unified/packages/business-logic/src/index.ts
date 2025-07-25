import {
  AttendanceRecord,
  LeaveRecord,
  ReimbursementRecord,
  TaxCalculationRequest,
  TaxCalculationResponse,
  LocationData
} from '@pmssrc/shared-types';

// Business logic utilities for PMSSRC applications

export class AttendanceCalculator {
  /**
   * Calculate working hours from attendance records
   */
  static calculateWorkingHours(attendanceRecords: AttendanceRecord[]): number {
    let totalHours = 0;
    
    for (const record of attendanceRecords) {
      if (record.check_in_time && record.check_out_time) {
        const checkIn = new Date(record.check_in_time);
        const checkOut = new Date(record.check_out_time);
        const hours = (checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60);
        totalHours += hours;
      }
    }
    
    return totalHours;
  }

  /**
   * Calculate overtime hours (assuming 8 hours is standard workday)
   */
  static calculateOvertimeHours(attendanceRecords: AttendanceRecord[]): number {
    const totalHours = this.calculateWorkingHours(attendanceRecords);
    const standardHours = attendanceRecords.length * 8; // 8 hours per day
    return Math.max(0, totalHours - standardHours);
  }

  /**
   * Check if attendance is late (after 9:00 AM)
   */
  static isLateAttendance(checkInTime: string): boolean {
    const checkIn = new Date(checkInTime);
    const standardTime = new Date(checkIn);
    standardTime.setHours(9, 0, 0, 0); // 9:00 AM
    
    return checkIn > standardTime;
  }

  /**
   * Calculate attendance percentage for a given period
   */
  static calculateAttendancePercentage(
    attendanceRecords: AttendanceRecord[],
    totalWorkingDays: number
  ): number {
    const presentDays = attendanceRecords.filter(record => 
      record.status === 'PRESENT' || record.status === 'LATE'
    ).length;
    
    return (presentDays / totalWorkingDays) * 100;
  }
}

export class LeaveCalculator {
  /**
   * Calculate leave balance for a user
   */
  static calculateLeaveBalance(
    totalLeaves: number,
    usedLeaves: LeaveRecord[]
  ): number {
    const usedDays = usedLeaves
      .filter(leave => leave.status === 'APPROVED')
      .reduce((total, leave) => {
        const start = new Date(leave.start_date);
        const end = new Date(leave.end_date);
        const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
        return total + days;
      }, 0);
    
    return totalLeaves - usedDays;
  }

  /**
   * Calculate leave duration in days
   */
  static calculateLeaveDuration(startDate: string, endDate: string): number {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
  }

  /**
   * Check if leave dates overlap with existing approved leaves
   */
  static hasLeaveOverlap(
    newStartDate: string,
    newEndDate: string,
    existingLeaves: LeaveRecord[]
  ): boolean {
    const newStart = new Date(newStartDate);
    const newEnd = new Date(newEndDate);
    
    return existingLeaves
      .filter(leave => leave.status === 'APPROVED')
      .some(leave => {
        const existingStart = new Date(leave.start_date);
        const existingEnd = new Date(leave.end_date);
        
        return (newStart <= existingEnd && newEnd >= existingStart);
      });
  }
}

export class ReimbursementCalculator {
  /**
   * Calculate total reimbursement amount for a period
   */
  static calculateTotalReimbursement(
    reimbursements: ReimbursementRecord[],
    startDate?: string,
    endDate?: string
  ): number {
    let filteredReimbursements = reimbursements;
    
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      filteredReimbursements = reimbursements.filter(reimbursement => {
        const reimbursementDate = new Date(reimbursement.date);
        return reimbursementDate >= start && reimbursementDate <= end;
      });
    }
    
    return filteredReimbursements
      .filter(reimbursement => reimbursement.status === 'APPROVED')
      .reduce((total, reimbursement) => total + reimbursement.amount, 0);
  }

  /**
   * Calculate pending reimbursement amount
   */
  static calculatePendingReimbursement(reimbursements: ReimbursementRecord[]): number {
    return reimbursements
      .filter(reimbursement => reimbursement.status === 'PENDING')
      .reduce((total, reimbursement) => total + reimbursement.amount, 0);
  }
}

export class TaxCalculator {
  /**
   * Calculate basic tax based on income slabs
   */
  static calculateBasicTax(taxableIncome: number): number {
    if (taxableIncome <= 250000) return 0;
    if (taxableIncome <= 500000) return (taxableIncome - 250000) * 0.05;
    if (taxableIncome <= 1000000) return 12500 + (taxableIncome - 500000) * 0.2;
    return 112500 + (taxableIncome - 1000000) * 0.3;
  }

  /**
   * Calculate total deductions
   */
  static calculateTotalDeductions(deductions: any[]): number {
    return deductions.reduce((total, deduction) => total + deduction.amount, 0);
  }

  /**
   * Calculate effective tax rate
   */
  static calculateEffectiveTaxRate(taxLiability: number, grossIncome: number): number {
    return grossIncome > 0 ? (taxLiability / grossIncome) * 100 : 0;
  }

  /**
   * Calculate tax response
   */
  static calculateTaxResponse(taxRequest: TaxCalculationRequest): TaxCalculationResponse {
    const totalDeductions = this.calculateTotalDeductions(taxRequest.deductions);
    const grossIncome = taxRequest.basic_salary + taxRequest.allowances + (taxRequest.additional_income || 0);
    const taxableIncome = Math.max(0, grossIncome - totalDeductions);
    const taxLiability = this.calculateBasicTax(taxableIncome);
    const effectiveTaxRate = this.calculateEffectiveTaxRate(taxLiability, grossIncome);

    return {
      user_id: taxRequest.user_id,
      financial_year: taxRequest.financial_year,
      gross_income: grossIncome,
      total_deductions: totalDeductions,
      taxable_income: taxableIncome,
      tax_liability: taxLiability,
      effective_tax_rate: effectiveTaxRate,
      old_regime_tax: taxLiability,
      new_regime_tax: taxLiability * 0.9, // Simplified calculation
      recommended_regime: taxLiability > taxLiability * 0.9 ? 'NEW' : 'OLD',
      potential_savings: Math.abs(taxLiability - taxLiability * 0.9)
    };
  }
}

export class LocationValidator {
  /**
   * Check if user is within office geofence
   */
  static isWithinOfficeGeofence(
    userLocation: LocationData,
    officeLocation: LocationData,
    radiusInMeters: number = 100
  ): boolean {
    const distance = this.calculateDistance(userLocation, officeLocation);
    return distance <= radiusInMeters;
  }

  /**
   * Calculate distance between two locations using Haversine formula
   */
  static calculateDistance(location1: LocationData, location2: LocationData): number {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = (location1.latitude * Math.PI) / 180;
    const φ2 = (location2.latitude * Math.PI) / 180;
    const Δφ = ((location2.latitude - location1.latitude) * Math.PI) / 180;
    const Δλ = ((location2.longitude - location1.longitude) * Math.PI) / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distance in meters
  }

  /**
   * Check if location accuracy is sufficient
   */
  static isLocationAccurate(location: LocationData, requiredAccuracy: number = 10): boolean {
    return location.accuracy ? location.accuracy <= requiredAccuracy : true;
  }
}

export class DateUtils {
  /**
   * Check if date is a working day (Monday to Friday)
   */
  static isWorkingDay(date: Date): boolean {
    const day = date.getDay();
    return day >= 1 && day <= 5; // Monday = 1, Friday = 5
  }

  /**
   * Get number of working days between two dates
   */
  static getWorkingDays(startDate: Date, endDate: Date): number {
    let workingDays = 0;
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      if (this.isWorkingDay(currentDate)) {
        workingDays++;
      }
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return workingDays;
  }

  /**
   * Format date in various formats
   */
  static formatDate(date: Date, format: 'short' | 'long' | 'iso' = 'short'): string {
    switch (format) {
      case 'short':
        return date.toLocaleDateString();
      case 'long':
        return date.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      case 'iso':
        return date.toISOString();
      default:
        return date.toLocaleDateString();
    }
  }

  /**
   * Get current financial year
   */
  static getCurrentFinancialYear(): string {
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;
    
    if (currentMonth >= 4) {
      return `${currentYear}-${currentYear + 1}`;
    } else {
      return `${currentYear - 1}-${currentYear}`;
    }
  }
}

export class ValidationUtils {
  /**
   * Validate email format
   */
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate phone number format
   */
  static isValidPhoneNumber(phone: string): boolean {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
  }

  /**
   * Validate required fields
   */
  static validateRequiredFields(data: any, requiredFields: string[]): string[] {
    const missingFields: string[] = [];
    
    for (const field of requiredFields) {
      if (!data[field] || data[field] === '') {
        missingFields.push(field);
      }
    }
    
    return missingFields;
  }
} 