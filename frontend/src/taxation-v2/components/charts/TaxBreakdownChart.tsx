import React, { useState } from 'react';
import {
  Box,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  useTheme,
  useMediaQuery,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import {
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
  TrendingUp,
  AccountBalance,
  Receipt,
  Payment
} from '@mui/icons-material';

import { Card } from '../ui';
import { formatCurrency, formatPercentage } from '../../../shared/utils/formatting';

// =============================================================================
// INTERFACES & TYPES
// =============================================================================

interface TaxBreakdownData {
  income_tax: number;
  surcharge: number;
  cess: number;
  total_deductions: number;
  net_income: number;
  gross_income: number;
}

interface IncomeSourceData {
  source: string;
  amount: number;
  percentage: number;
  color: string;
}

interface TaxBreakdownChartProps {
  data: TaxBreakdownData;
  incomeSources?: IncomeSourceData[];
  title?: string;
  showComparison?: boolean;
  comparisonData?: TaxBreakdownData;
  height?: number;
}

type ChartType = 'pie' | 'bar' | 'donut';

// =============================================================================
// CHART COLORS
// =============================================================================

const TAX_COLORS = {
  income_tax: '#2196F3',
  surcharge: '#FF9800', 
  cess: '#F44336',
  deductions: '#4CAF50',
  net_income: '#00BCD4',
  gross_income: '#9C27B0'
};

const INCOME_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
  '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD'
];

// =============================================================================
// TAX BREAKDOWN CHART COMPONENT
// =============================================================================

export const TaxBreakdownChart: React.FC<TaxBreakdownChartProps> = ({
  data,
  incomeSources = [],
  title = 'Tax Breakdown Analysis',
  showComparison = false,
  comparisonData,
  height = 400
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [chartType, setChartType] = useState<ChartType>('pie');
  const [activeSection, setActiveSection] = useState<string | null>(null);

  // =============================================================================
  // DATA PREPARATION
  // =============================================================================

  const prepareTaxData = () => [
    {
      name: 'Income Tax',
      value: data.income_tax,
      color: TAX_COLORS.income_tax,
      percentage: (data.income_tax / data.gross_income) * 100
    },
    {
      name: 'Surcharge',
      value: data.surcharge,
      color: TAX_COLORS.surcharge,
      percentage: (data.surcharge / data.gross_income) * 100
    },
    {
      name: 'Education Cess',
      value: data.cess,
      color: TAX_COLORS.cess,
      percentage: (data.cess / data.gross_income) * 100
    },
    {
      name: 'Net Income',
      value: data.net_income,
      color: TAX_COLORS.net_income,
      percentage: (data.net_income / data.gross_income) * 100
    }
  ].filter(item => item.value > 0);

  const prepareBarData = () => {
    const baseData = [
      { name: 'Gross Income', value: data.gross_income, color: TAX_COLORS.gross_income },
      { name: 'Total Tax', value: data.income_tax + data.surcharge + data.cess, color: TAX_COLORS.income_tax },
      { name: 'Deductions', value: data.total_deductions, color: TAX_COLORS.deductions },
      { name: 'Net Income', value: data.net_income, color: TAX_COLORS.net_income }
    ];

    if (showComparison && comparisonData) {
      return baseData.map(item => ({
        ...item,
        comparison: getComparisonValue(item.name, comparisonData)
      }));
    }

    return baseData;
  };

  const getComparisonValue = (name: string, compareData: TaxBreakdownData) => {
    switch (name) {
      case 'Gross Income': return compareData.gross_income;
      case 'Total Tax': return compareData.income_tax + compareData.surcharge + compareData.cess;
      case 'Deductions': return compareData.total_deductions;
      case 'Net Income': return compareData.net_income;
      default: return 0;
    }
  };

  // =============================================================================
  // CHART RENDERERS
  // =============================================================================

  const renderPieChart = () => {
    const pieData = prepareTaxData();
    
    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
            outerRadius={isMobile ? 60 : 80}
            fill="#8884d8"
            dataKey="value"
            onMouseEnter={(_, index) => setActiveSection(pieData[index]?.name || null)}
            onMouseLeave={() => setActiveSection(null)}
          >
            {pieData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color}
                stroke={activeSection === entry.name ? theme.palette.primary.main : 'none'}
                strokeWidth={activeSection === entry.name ? 3 : 0}
              />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => [formatCurrency(value), 'Amount']}
            labelFormatter={(label) => `${label}`}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderDonutChart = () => {
    const pieData = prepareTaxData();
    
    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={isMobile ? 70 : 90}
            innerRadius={isMobile ? 35 : 45}
            fill="#8884d8"
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => [formatCurrency(value), 'Amount']}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderBarChart = () => {
    const barData = prepareBarData();
    
    return (
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="name" 
            angle={isMobile ? -45 : 0}
            textAnchor={isMobile ? 'end' : 'middle'}
            height={isMobile ? 80 : 60}
          />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value, { compact: true })}
          />
          <Tooltip 
            formatter={(value: number) => [formatCurrency(value), 'Amount']}
          />
          <Bar dataKey="value" fill={TAX_COLORS.income_tax} />
          {showComparison && (
            <Bar dataKey="comparison" fill={TAX_COLORS.surcharge} />
          )}
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderChart = () => {
    switch (chartType) {
      case 'pie': return renderPieChart();
      case 'donut': return renderDonutChart();
      case 'bar': return renderBarChart();
      default: return renderPieChart();
    }
  };

  // =============================================================================
  // UI RENDERERS
  // =============================================================================

  const renderChartControls = () => (
    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
      <ToggleButtonGroup
        value={chartType}
        exclusive
        onChange={(_, newType) => newType && setChartType(newType)}
        size={isMobile ? 'small' : 'medium'}
      >
        <ToggleButton value="pie">
          <PieChartIcon sx={{ mr: 1 }} />
          {!isMobile && 'Pie'}
        </ToggleButton>
        <ToggleButton value="donut">
          <PieChartIcon sx={{ mr: 1 }} />
          {!isMobile && 'Donut'}
        </ToggleButton>
        <ToggleButton value="bar">
          <BarChartIcon sx={{ mr: 1 }} />
          {!isMobile && 'Bar'}
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );

  const renderTaxSummary = () => {
    const totalTax = data.income_tax + data.surcharge + data.cess;
    const effectiveRate = (totalTax / data.gross_income) * 100;
    
    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
          <Card variant="info">
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <AccountBalance sx={{ fontSize: 32, color: 'info.main', mb: 1 }} />
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(data.gross_income)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Gross Income
              </Typography>
            </Box>
          </Card>
        </Box>
        
        <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
          <Card variant="error">
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Payment sx={{ fontSize: 32, color: 'error.main', mb: 1 }} />
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(totalTax)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Tax
              </Typography>
            </Box>
          </Card>
        </Box>
        
        <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
          <Card variant="success">
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Receipt sx={{ fontSize: 32, color: 'success.main', mb: 1 }} />
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(data.total_deductions)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Deductions
              </Typography>
            </Box>
          </Card>
        </Box>
        
        <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
          <Card variant="outlined">
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <TrendingUp sx={{ fontSize: 32, color: 'primary.main', mb: 1 }} />
              <Typography variant="h6" fontWeight="bold">
                {formatPercentage(effectiveRate)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Effective Rate
              </Typography>
            </Box>
          </Card>
        </Box>
      </Box>
    );
  };

  const renderIncomeSourcesChart = () => {
    if (!incomeSources.length) return null;

    return (
      <Card title="Income Sources Breakdown" variant="outlined" sx={{ mt: 3 }}>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={incomeSources}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ source, percentage }) => `${source}: ${percentage.toFixed(1)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="amount"
            >
              {incomeSources.map((_, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={INCOME_COLORS[index % INCOME_COLORS.length]} 
                />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value: number) => [formatCurrency(value), 'Amount']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Card>
    );
  };

  const renderDetailsList = () => {
    const taxDetails = [
      { label: 'Basic Income Tax', amount: data.income_tax, color: TAX_COLORS.income_tax },
      { label: 'Surcharge', amount: data.surcharge, color: TAX_COLORS.surcharge },
      { label: 'Education Cess', amount: data.cess, color: TAX_COLORS.cess },
    ].filter(item => item.amount > 0);

    return (
      <Card title="Tax Components" variant="outlined" sx={{ mt: 3 }}>
        <List dense>
          {taxDetails.map((item, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <Box 
                  sx={{ 
                    width: 12, 
                    height: 12, 
                    borderRadius: '50%', 
                    backgroundColor: item.color 
                  }} 
                />
              </ListItemIcon>
              <ListItemText 
                primary={item.label}
                secondary={`${formatPercentage((item.amount / data.gross_income) * 100)} of gross income`}
              />
              <Chip 
                label={formatCurrency(item.amount)} 
                size="small" 
                variant="outlined" 
              />
            </ListItem>
          ))}
        </List>
      </Card>
    );
  };

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        {title}
      </Typography>
      
      {/* Tax Summary Cards */}
      {renderTaxSummary()}
      
      {/* Chart Section */}
      <Card sx={{ mt: 3 }}>
        {renderChartControls()}
        <Box sx={{ height: height }}>
          {renderChart()}
        </Box>
      </Card>
      
      {/* Income Sources */}
      {renderIncomeSourcesChart()}
      
      {/* Details List */}
      {renderDetailsList()}
    </Box>
  );
};

export default TaxBreakdownChart; 