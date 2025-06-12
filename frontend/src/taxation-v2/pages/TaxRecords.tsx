import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  useTheme,
  useMediaQuery,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  History,
  FileDownload,
  Calculate,
  FilterList,
  Refresh
} from '@mui/icons-material';

import { Card, Button } from '../components/ui';
import { TaxRecordsTable } from '../components/tables/TaxRecordsTable';
import { TaxExportManager } from '../components/export/TaxExportManager';
import { formatCurrency } from '../../shared/utils/formatting';

// =============================================================================
// INTERFACES
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

// =============================================================================
// MOCK DATA
// =============================================================================

const generateMockRecords = (): TaxRecord[] => {
  const currentYear = new Date().getFullYear();
  const records: TaxRecord[] = [];
  
  for (let i = 0; i < 5; i++) {
    const year = (currentYear - i).toString();
    const baseIncome = 1200000 + (i * 100000);
    const regime = i < 2 ? 'new' : 'old';
    
    records.push({
      id: `record-${year}`,
      year,
      income_sources: [
        {
          type: 'salary',
          amount: baseIncome * 0.8,
          description: 'Software Engineer Salary'
        },
        {
          type: 'freelance',
          amount: baseIncome * 0.2,
          description: 'Consulting Income'
        }
      ],
      deductions: {
        section_80c: 150000,
        section_80d: 25000,
        other: 50000,
        total: 225000
      },
      tax_calculation: {
        gross_income: baseIncome,
        taxable_income: baseIncome - 225000,
        income_tax: regime === 'new' ? (baseIncome * 0.12) : (baseIncome * 0.14),
        surcharge: regime === 'new' ? 0 : (baseIncome * 0.01),
        cess: regime === 'new' ? (baseIncome * 0.004) : (baseIncome * 0.005),
        total_tax: regime === 'new' ? (baseIncome * 0.124) : (baseIncome * 0.155),
        net_income: regime === 'new' ? (baseIncome * 0.876) : (baseIncome * 0.845)
      },
      regime,
      status: i === 0 ? 'calculated' : i === 1 ? 'filed' : 'draft',
      created_at: new Date(currentYear - i, 3, 15).toISOString(),
      updated_at: new Date(currentYear - i, 3, 20).toISOString()
    });
  }
  
  return records;
};

// =============================================================================
// TAX RECORDS COMPONENT
// =============================================================================

export const TaxRecords: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [records, setRecords] = useState<TaxRecord[]>([]);
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);



  // =============================================================================
  // EFFECTS
  // =============================================================================

  useEffect(() => {
    // Simulate loading records
    const loadRecords = async () => {
      setIsLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setRecords(generateMockRecords());
      setIsLoading(false);
    };
    
    loadRecords();
  }, []);

  // =============================================================================
  // CALCULATIONS
  // =============================================================================

  const getRecordsSummary = () => {
    if (records.length === 0) {
      return {
        totalRecords: 0,
        totalIncome: 0,
        totalTax: 0,
        avgEffectiveRate: 0,
        latestYear: ''
      };
    }

    const totalIncome = records.reduce((sum, record) => sum + record.tax_calculation.gross_income, 0);
    const totalTax = records.reduce((sum, record) => sum + record.tax_calculation.total_tax, 0);
    const avgEffectiveRate = (totalTax / totalIncome) * 100;
    const latestYear = Math.max(...records.map(record => parseInt(record.year))).toString();

    return {
      totalRecords: records.length,
      totalIncome,
      totalTax,
      avgEffectiveRate,
      latestYear
    };
  };

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleExportRecords = (recordsToExport: TaxRecord[]) => {
    console.log('Exporting records:', recordsToExport);
    setIsExportDialogOpen(true);
  };

  const handleNewCalculation = () => {
    console.log('Starting new calculation...');
    // Navigate to calculator
  };

  const handleRefreshData = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRecords(generateMockRecords());
    setIsLoading(false);
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderSummaryCards = () => {
    const summary = getRecordsSummary();

    if (isLoading) {
      return (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} loading />
          ))}
        </Box>
      );
    }

    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
        <Card variant="info">
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <History sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" fontWeight="bold">
              {summary.totalRecords}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Records
            </Typography>
          </Box>
        </Card>

        <Card variant="success">
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" fontWeight="bold">
              {formatCurrency(summary.totalIncome)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Income
            </Typography>
            <Typography variant="caption" color="success.main">
              Across all years
            </Typography>
          </Box>
        </Card>

        <Card variant="error">
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" fontWeight="bold">
              {formatCurrency(summary.totalTax)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Tax Paid
            </Typography>
            <Typography variant="caption" color="error.main">
              Cumulative tax
            </Typography>
          </Box>
        </Card>

        <Card variant="outlined">
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" fontWeight="bold">
              {summary.avgEffectiveRate.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg. Effective Rate
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Across all years
            </Typography>
          </Box>
        </Card>
      </Box>
    );
  };

  const renderQuickActions = () => (
    <Card title="Quick Actions" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<Calculate />}
          onClick={handleNewCalculation}
          fullWidth
        >
          New Calculation
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={() => handleExportRecords(records)}
          fullWidth
          disabled={records.length === 0}
        >
          Export All
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={handleRefreshData}
          fullWidth
        >
          Refresh Data
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<FilterList />}
          fullWidth
        >
          Advanced Filters
        </Button>
      </Box>
    </Card>
  );

  const renderSpeedDial = () => {
    if (!isMobile) return null;

    const actions = [
      { icon: <Calculate />, name: 'New Calculation', onClick: handleNewCalculation },
      { icon: <FileDownload />, name: 'Export', onClick: () => handleExportRecords(records) },
      { icon: <Refresh />, name: 'Refresh', onClick: handleRefreshData },
    ];

    return (
      <SpeedDial
        ariaLabel="Records Actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        {actions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.onClick}
          />
        ))}
      </SpeedDial>
    );
  };

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            <History sx={{ mr: 2, verticalAlign: 'middle' }} />
            Tax Records
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and analyze your historical tax calculations
          </Typography>
        </Box>

        {renderSummaryCards()}
        
        <Box sx={{ mt: 4 }}>
          <Card loading />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          <History sx={{ mr: 2, verticalAlign: 'middle' }} />
          Tax Records
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage and analyze your historical tax calculations
        </Typography>
      </Box>

      {/* Summary Cards */}
      {renderSummaryCards()}

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        {renderQuickActions()}
      </Box>

      {/* Records Table */}
      <Box sx={{ mt: 4 }}>
        <TaxRecordsTable
          data={records}
          loading={isLoading}
        />
      </Box>

      {/* Export Dialog */}
      <TaxExportManager
        open={isExportDialogOpen}
        onClose={() => setIsExportDialogOpen(false)}
        records={records}
      />

      {/* Mobile Speed Dial */}
      {renderSpeedDial()}
    </Container>
  );
};

export default TaxRecords; 