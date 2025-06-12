import BaseAPI from './baseApi';
import * as Types from '../types/api';

class TaxationAPI extends BaseAPI {
  constructor() {
    super({
      baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }

  // =============================================================================
  // COMPREHENSIVE TAX CALCULATION ENDPOINTS
  // =============================================================================

  /**
   * Calculate comprehensive tax including all income sources and components
   */
  async calculateComprehensiveTax(
    input: Types.ComprehensiveTaxInputDTO
  ): Promise<Types.PeriodicTaxCalculationResponseDTO> {
    try {
      return await this.post('/api/v1/taxation/calculate-comprehensive', input);
    } catch (error) {
      console.error('Error calculating comprehensive tax:', error);
      throw error;
    }
  }

  // =============================================================================
  // COMPONENT-SPECIFIC CALCULATION ENDPOINTS
  // =============================================================================

  /**
   * Calculate perquisites tax impact only
   */
  async calculatePerquisites(
    perquisites: Types.PerquisitesDTO,
    regimeType: Types.TaxRegime
  ): Promise<any> {
    try {
      return await this.post(
        `/api/v1/taxation/perquisites/calculate?regime_type=${regimeType}`,
        perquisites
      );
    } catch (error) {
      console.error('Error calculating perquisites:', error);
      throw error;
    }
  }

  /**
   * Calculate house property income tax
   */
  async calculateHouseProperty(
    houseProperty: Types.HousePropertyIncomeDTO,
    regimeType: Types.TaxRegime
  ): Promise<any> {
    try {
      return await this.post(
        `/api/v1/taxation/house-property/calculate?regime_type=${regimeType}`,
        houseProperty
      );
    } catch (error) {
      console.error('Error calculating house property income:', error);
      throw error;
    }
  }

  /**
   * Calculate capital gains tax
   */
  async calculateCapitalGains(
    capitalGains: Types.CapitalGainsIncomeDTO,
    regimeType: Types.TaxRegime
  ): Promise<any> {
    try {
      return await this.post(
        `/api/v1/taxation/capital-gains/calculate?regime_type=${regimeType}`,
        capitalGains
      );
    } catch (error) {
      console.error('Error calculating capital gains:', error);
      throw error;
    }
  }

  // =============================================================================
  // RECORD MANAGEMENT ENDPOINTS
  // =============================================================================

  /**
   * Create a new taxation record
   */
  async createRecord(
    request: Types.CreateTaxationRecordRequest
  ): Promise<Types.CreateTaxationRecordResponse> {
    try {
      return await this.post('/api/v1/taxation/records', request);
    } catch (error) {
      console.error('Error creating taxation record:', error);
      throw error;
    }
  }

  /**
   * Get list of taxation records with optional filters
   */
  async listRecords(
    query?: Types.TaxationRecordQuery
  ): Promise<Types.TaxationRecordListResponse> {
    try {
      const params = query ? new URLSearchParams(
        Object.entries(query).reduce((acc, [key, value]) => {
          if (value !== undefined && value !== null) {
            acc[key] = value.toString();
          }
          return acc;
        }, {} as Record<string, string>)
      ) : undefined;

      const url = params ? `/api/v1/taxation/records?${params}` : '/api/v1/taxation/records';
      return await this.get(url);
    } catch (error) {
      console.error('Error listing taxation records:', error);
      throw error;
    }
  }

  /**
   * Get taxation record by ID
   */
  async getRecord(taxationId: string): Promise<Types.TaxationRecordSummaryDTO> {
    try {
      return await this.get(`/api/v1/taxation/records/${taxationId}`);
    } catch (error) {
      console.error('Error getting taxation record:', error);
      throw error;
    }
  }

  // =============================================================================
  // INFORMATION AND UTILITY ENDPOINTS
  // =============================================================================

  /**
   * Get comparison between old and new tax regimes
   */
  async getTaxRegimeComparison(): Promise<any> {
    try {
      return await this.get('/api/v1/taxation/tax-regimes/comparison');
    } catch (error) {
      console.error('Error getting tax regime comparison:', error);
      throw error;
    }
  }

  /**
   * Get available tax years for selection
   */
  async getAvailableTaxYears(): Promise<Types.TaxYearInfoDTO[]> {
    try {
      return await this.get('/api/v1/taxation/tax-years');
    } catch (error) {
      console.error('Error getting available tax years:', error);
      throw error;
    }
  }

  /**
   * Check taxation service health
   */
  async healthCheck(): Promise<Types.HealthCheckResponse> {
    try {
      return await this.get('/api/v1/taxation/health');
    } catch (error) {
      console.error('Error checking taxation service health:', error);
      throw error;
    }
  }
}

// Create and export a singleton instance
const taxationApi = new TaxationAPI();
export default taxationApi;

// Also export the class for testing or custom instances
export { TaxationAPI }; 