import React, { useState } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Typography,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import {
  FileDownload,
  PictureAsPdf,
  TableChart,
  Assignment
} from '@mui/icons-material';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';

import { Button, Card } from '../ui';
import { formatCurrency, formatDate, formatPercentage } from '../../../shared/utils/formatting';

// =============================================================================
// INTERFACES & TYPES
// =============================================================================

interface TaxRecord {
  id: string;
  year: string;
  income_sources: Array<{
    type: string;
    amount: number;
    description: string;
  }>;
  deductions: {
    section_80c: number;
    section_80d: number;
    other: number;
    total: number;
  };
  tax_calculation: {
    gross_income: number;
    taxable_income: number;
    income_tax: number;
    surcharge: number;
    cess: number;
    total_tax: number;
    net_income: number;
  };
  regime: 'old' | 'new';
  status: 'draft' | 'calculated' | 'filed' | 'revised';
  created_at: string;
  updated_at: string;
}

interface ExportOptions {
  format: 'excel' | 'pdf' | 'csv';
  includeBreakdown: boolean;
  includeCharts: boolean;
  dateRange: 'all' | 'last_year' | 'last_3_years' | 'custom';
  selectedRecords: string[];
}

interface TaxExportManagerProps {
  open: boolean;
  onClose: () => void;
  records: TaxRecord[];
  title?: string;
}

// =============================================================================
// EXPORT UTILITIES
// =============================================================================

class TaxDataExporter {
  static async exportToExcel(records: TaxRecord[], options: ExportOptions) {
    const workbook = XLSX.utils.book_new();
    
    // Summary Sheet
    const summaryData = records.map(record => ({
      'Tax Year': record.year,
      'Gross Income': record.tax_calculation.gross_income,
      'Total Deductions': record.deductions.total,
      'Taxable Income': record.tax_calculation.taxable_income,
      'Income Tax': record.tax_calculation.income_tax,
      'Surcharge': record.tax_calculation.surcharge,
      'Education Cess': record.tax_calculation.cess,
      'Total Tax': record.tax_calculation.total_tax,
      'Net Income': record.tax_calculation.net_income,
      'Effective Rate (%)': ((record.tax_calculation.total_tax / record.tax_calculation.gross_income) * 100).toFixed(2),
      'Tax Regime': record.regime.toUpperCase(),
      'Status': record.status,
      'Last Updated': formatDate(record.updated_at)
    }));
    
    const summarySheet = XLSX.utils.json_to_sheet(summaryData);
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Tax Summary');
    
    // Detailed Breakdown Sheet (if requested)
    if (options.includeBreakdown) {
      const detailedData: any[] = [];
      
      records.forEach(record => {
        // Income Sources
        record.income_sources.forEach(source => {
          detailedData.push({
            'Tax Year': record.year,
            'Category': 'Income',
            'Sub-Category': source.type.replace('_', ' ').toUpperCase(),
            'Description': source.description,
            'Amount': source.amount,
            'Type': 'Income Source'
          });
        });
        
        // Deductions
        if (record.deductions.section_80c > 0) {
          detailedData.push({
            'Tax Year': record.year,
            'Category': 'Deduction',
            'Sub-Category': 'Section 80C',
            'Description': 'Section 80C Deductions',
            'Amount': record.deductions.section_80c,
            'Type': 'Tax Deduction'
          });
        }
        
        if (record.deductions.section_80d > 0) {
          detailedData.push({
            'Tax Year': record.year,
            'Category': 'Deduction',
            'Sub-Category': 'Section 80D',
            'Description': 'Health Insurance Premium',
            'Amount': record.deductions.section_80d,
            'Type': 'Tax Deduction'
          });
        }
        
        if (record.deductions.other > 0) {
          detailedData.push({
            'Tax Year': record.year,
            'Category': 'Deduction',
            'Sub-Category': 'Other',
            'Description': 'Other Deductions',
            'Amount': record.deductions.other,
            'Type': 'Tax Deduction'
          });
        }
      });
      
      const detailedSheet = XLSX.utils.json_to_sheet(detailedData);
      XLSX.utils.book_append_sheet(workbook, detailedSheet, 'Detailed Breakdown');
    }
    
    // Comparison Sheet
    if (records.length > 1) {
      const comparisonData = records.map((record, index) => {
        const prevRecord = index > 0 ? records[index - 1] : null;
        const incomeGrowth = prevRecord 
          ? ((record.tax_calculation.gross_income - prevRecord.tax_calculation.gross_income) / prevRecord.tax_calculation.gross_income) * 100
          : 0;
        const taxGrowth = prevRecord
          ? ((record.tax_calculation.total_tax - prevRecord.tax_calculation.total_tax) / prevRecord.tax_calculation.total_tax) * 100
          : 0;
        
        return {
          'Tax Year': record.year,
          'Gross Income': record.tax_calculation.gross_income,
          'Income Growth (%)': incomeGrowth.toFixed(2),
          'Total Tax': record.tax_calculation.total_tax,
          'Tax Growth (%)': taxGrowth.toFixed(2),
          'Tax Savings vs Previous Year': prevRecord ? (prevRecord.tax_calculation.total_tax - record.tax_calculation.total_tax) : 0,
          'Effective Rate (%)': ((record.tax_calculation.total_tax / record.tax_calculation.gross_income) * 100).toFixed(2)
        };
      });
      
      const comparisonSheet = XLSX.utils.json_to_sheet(comparisonData);
      XLSX.utils.book_append_sheet(workbook, comparisonSheet, 'Year-over-Year Comparison');
    }
    
    // Download
    const fileName = `tax-records-${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(workbook, fileName);
  }
  
  static async exportToPDF(records: TaxRecord[], _options: ExportOptions) {
    const pdf = new jsPDF();
    const pageWidth = pdf.internal.pageSize.width;
    const pageHeight = pdf.internal.pageSize.height;
    let yPosition = 20;
    
    // Title
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Tax Records Report', pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 20;
    
    // Generation Date
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Generated on: ${formatDate(new Date().toISOString())}`, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 20;
    
    // Summary Statistics
    const totalIncome = records.reduce((sum, r) => sum + r.tax_calculation.gross_income, 0);
    const totalTax = records.reduce((sum, r) => sum + r.tax_calculation.total_tax, 0);
    const avgEffectiveRate = records.length > 0 ? (totalTax / totalIncome) * 100 : 0;
    
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Summary Statistics', 20, yPosition);
    yPosition += 15;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Total Records: ${records.length}`, 20, yPosition);
    yPosition += 10;
    pdf.text(`Total Income: ${formatCurrency(totalIncome)}`, 20, yPosition);
    yPosition += 10;
    pdf.text(`Total Tax: ${formatCurrency(totalTax)}`, 20, yPosition);
    yPosition += 10;
    pdf.text(`Average Effective Rate: ${formatPercentage(avgEffectiveRate)}`, 20, yPosition);
    yPosition += 20;
    
    // Records Table
    records.forEach((record) => {
      if (yPosition > pageHeight - 60) {
        pdf.addPage();
        yPosition = 20;
      }
      
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      pdf.text(`Tax Year ${record.year}`, 20, yPosition);
      yPosition += 15;
      
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      
      const data = [
        ['Gross Income:', formatCurrency(record.tax_calculation.gross_income)],
        ['Total Deductions:', formatCurrency(record.deductions.total)],
        ['Taxable Income:', formatCurrency(record.tax_calculation.taxable_income)],
        ['Income Tax:', formatCurrency(record.tax_calculation.income_tax)],
        ['Surcharge:', formatCurrency(record.tax_calculation.surcharge)],
        ['Education Cess:', formatCurrency(record.tax_calculation.cess)],
        ['Total Tax:', formatCurrency(record.tax_calculation.total_tax)],
        ['Net Income:', formatCurrency(record.tax_calculation.net_income)],
        ['Tax Regime:', record.regime.toUpperCase()],
        ['Status:', record.status.toUpperCase()]
      ];
      
      data.forEach(([label, value]) => {
        if (label && value) {
          pdf.text(label, 25, yPosition);
          pdf.text(value, 100, yPosition);
          yPosition += 8;
        }
      });
      
      yPosition += 10;
    });
    
    // Download
    const fileName = `tax-records-${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(fileName);
  }
  
  static async exportToCSV(records: TaxRecord[], _options: ExportOptions) {
    const headers = [
      'Tax Year',
      'Gross Income',
      'Total Deductions',
      'Taxable Income',
      'Income Tax',
      'Surcharge',
      'Education Cess',
      'Total Tax',
      'Net Income',
      'Effective Rate (%)',
      'Tax Regime',
      'Status',
      'Created Date',
      'Last Updated'
    ];
    
    const csvData = records.map(record => [
      record.year,
      record.tax_calculation.gross_income,
      record.deductions.total,
      record.tax_calculation.taxable_income,
      record.tax_calculation.income_tax,
      record.tax_calculation.surcharge,
      record.tax_calculation.cess,
      record.tax_calculation.total_tax,
      record.tax_calculation.net_income,
      ((record.tax_calculation.total_tax / record.tax_calculation.gross_income) * 100).toFixed(2),
      record.regime.toUpperCase(),
      record.status,
      formatDate(record.created_at),
      formatDate(record.updated_at)
    ]);
    
    const csvContent = [headers, ...csvData]
      .map(row => row.join(','))
      .join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tax-records-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const TaxExportManager: React.FC<TaxExportManagerProps> = ({
  open,
  onClose,
  records,
  title = 'Export Tax Records'
}) => {
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'excel',
    includeBreakdown: true,
    includeCharts: false,
    dateRange: 'all',
    selectedRecords: []
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);
    
    try {
      const filteredRecords = exportOptions.selectedRecords.length > 0
        ? records.filter(record => exportOptions.selectedRecords.includes(record.id))
        : records;
      
      switch (exportOptions.format) {
        case 'excel':
          await TaxDataExporter.exportToExcel(filteredRecords, exportOptions);
          break;
        case 'pdf':
          await TaxDataExporter.exportToPDF(filteredRecords, exportOptions);
          break;
        case 'csv':
          await TaxDataExporter.exportToCSV(filteredRecords, exportOptions);
          break;
      }
      
      onClose();
    } catch (error) {
      setExportError('Failed to export data. Please try again.');
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const getExportIcon = () => {
    switch (exportOptions.format) {
      case 'pdf': return <PictureAsPdf />;
      case 'csv': return <Assignment />;
      default: return <TableChart />;
    }
  };

  const getFormatDescription = () => {
    switch (exportOptions.format) {
      case 'excel':
        return 'Export as Excel spreadsheet with multiple sheets for summary, breakdown, and comparison data.';
      case 'pdf':
        return 'Export as PDF document with formatted tables and summary statistics.';
      case 'csv':
        return 'Export as CSV file for importing into other applications.';
      default:
        return '';
    }
  };

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FileDownload />
          {title}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Export Format */}
          <Box>
            <FormControl fullWidth>
              <InputLabel>Export Format</InputLabel>
              <Select
                value={exportOptions.format}
                label="Export Format"
                onChange={(e) => setExportOptions(prev => ({ 
                  ...prev, 
                  format: e.target.value as 'excel' | 'pdf' | 'csv' 
                }))}
              >
                <MenuItem value="excel">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TableChart />
                    Excel Spreadsheet (.xlsx)
                  </Box>
                </MenuItem>
                <MenuItem value="pdf">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PictureAsPdf />
                    PDF Document (.pdf)
                  </Box>
                </MenuItem>
                <MenuItem value="csv">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Assignment />
                    CSV File (.csv)
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Format Description */}
          <Box>
            <Card variant="info">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
                {getExportIcon()}
                <Typography variant="body2">
                  {getFormatDescription()}
                </Typography>
              </Box>
            </Card>
          </Box>

          {/* Export Options */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Export Options
            </Typography>
            
            <FormControlLabel
              control={
                <Checkbox
                  checked={exportOptions.includeBreakdown}
                  onChange={(e) => setExportOptions(prev => ({ 
                    ...prev, 
                    includeBreakdown: e.target.checked 
                  }))}
                />
              }
              label="Include detailed breakdown of income sources and deductions"
            />
            
            {exportOptions.format === 'pdf' && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={exportOptions.includeCharts}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      includeCharts: e.target.checked 
                    }))}
                  />
                }
                label="Include charts and graphs (PDF only)"
              />
            )}
          </Box>

          {/* Summary */}
          <Box>
            <Divider />
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Export Summary
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Records to export: {records.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Format: {exportOptions.format.toUpperCase()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Include breakdown: {exportOptions.includeBreakdown ? 'Yes' : 'No'}
              </Typography>
            </Box>
          </Box>

          {/* Error Display */}
          {exportError && (
            <Box>
              <Alert severity="error">{exportError}</Alert>
            </Box>
          )}
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={isExporting}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleExport}
          disabled={isExporting || records.length === 0}
          startIcon={isExporting ? <CircularProgress size={20} /> : <FileDownload />}
        >
          {isExporting ? 'Exporting...' : 'Export'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TaxExportManager; 