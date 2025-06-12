import React, { useState } from 'react';
import {
  Box,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  useTheme,
  useMediaQuery,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import {
  ShowChart,
  AreaChart as AreaChartIcon,
  DateRange
} from '@mui/icons-material';

import { Card } from '../ui';
import { formatCurrency, formatPercentage } from '../../../shared/utils/formatting';

// =============================================================================
// INTERFACES
// =============================================================================

interface TaxTrendData {
  year: string;
  gross_income: number;
  total_tax: number;
  net_income: number;
  effective_rate: number;
  deductions: number;
}

interface TaxTrendsChartProps {
  data: TaxTrendData[];
  title?: string;
  height?: number;
}

type ChartType = 'line' | 'area';
type TimeRange = '3years' | '5years' | 'all';

// =============================================================================
// CONSTANTS
// =============================================================================

const CHART_COLORS = {
  gross_income: '#2196F3',
  total_tax: '#F44336',
  net_income: '#4CAF50',
  effective_rate: '#FF9800',
  deductions: '#9C27B0'
};

// =============================================================================
// COMPONENT
// =============================================================================

export const TaxTrendsChart: React.FC<TaxTrendsChartProps> = ({
  data,
  title = 'Tax Trends Over Time',
  height = 400
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [chartType, setChartType] = useState<ChartType>('line');
  const [timeRange, setTimeRange] = useState<TimeRange>('5years');

  // =============================================================================
  // DATA PROCESSING
  // =============================================================================

  const getFilteredData = () => {
    if (timeRange === 'all') return data;
    
    const years = timeRange === '3years' ? 3 : 5;
    return data.slice(-years);
  };

  const getGrowthRate = (field: keyof TaxTrendData) => {
    const filteredData = getFilteredData();
    if (filteredData.length < 2) return 0;
    
    const firstItem = filteredData[0];
    const lastItem = filteredData[filteredData.length - 1];
    
    if (!firstItem || !lastItem) return 0;
    
    const firstValue = Number(firstItem[field]);
    const lastValue = Number(lastItem[field]);
    
    if (firstValue === 0) return 0;
    return ((lastValue - firstValue) / firstValue) * 100;
  };

  // =============================================================================
  // CHART RENDERERS
  // =============================================================================

  const renderLineChart = () => {
    const filteredData = getFilteredData();
    
    return (
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={filteredData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value, { compact: true })}
          />
          <Tooltip 
            formatter={(value: number, name: string) => [
              name === 'effective_rate' ? formatPercentage(value) : formatCurrency(value),
              name.replace('_', ' ').toUpperCase()
            ]}
            labelFormatter={(label) => `Year: ${label}`}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="gross_income" 
            stroke={CHART_COLORS.gross_income} 
            strokeWidth={2}
            name="Gross Income"
          />
          <Line 
            type="monotone" 
            dataKey="total_tax" 
            stroke={CHART_COLORS.total_tax} 
            strokeWidth={2}
            name="Total Tax"
          />
          <Line 
            type="monotone" 
            dataKey="net_income" 
            stroke={CHART_COLORS.net_income} 
            strokeWidth={2}
            name="Net Income"
          />
          <Line 
            type="monotone" 
            dataKey="deductions" 
            stroke={CHART_COLORS.deductions} 
            strokeWidth={2}
            name="Deductions"
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const renderAreaChart = () => {
    const filteredData = getFilteredData();
    
    return (
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={filteredData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value, { compact: true })}
          />
          <Tooltip 
            formatter={(value: number, name: string) => [
              name === 'effective_rate' ? formatPercentage(value) : formatCurrency(value),
              name.replace('_', ' ').toUpperCase()
            ]}
            labelFormatter={(label) => `Year: ${label}`}
          />
          <Legend />
          <Area 
            type="monotone" 
            dataKey="gross_income" 
            stackId="1"
            stroke={CHART_COLORS.gross_income} 
            fill={CHART_COLORS.gross_income}
            fillOpacity={0.3}
            name="Gross Income"
          />
          <Area 
            type="monotone" 
            dataKey="total_tax" 
            stackId="2"
            stroke={CHART_COLORS.total_tax} 
            fill={CHART_COLORS.total_tax}
            fillOpacity={0.3}
            name="Total Tax"
          />
          <Area 
            type="monotone" 
            dataKey="net_income" 
            stackId="3"
            stroke={CHART_COLORS.net_income} 
            fill={CHART_COLORS.net_income}
            fillOpacity={0.3}
            name="Net Income"
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  // =============================================================================
  // UI COMPONENTS
  // =============================================================================

  const renderControls = () => (
    <Box sx={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      flexDirection: isMobile ? 'column' : 'row',
      gap: 2,
      mb: 2 
    }}>
      <ToggleButtonGroup
        value={chartType}
        exclusive
        onChange={(_, newType) => newType && setChartType(newType)}
        size={isMobile ? 'small' : 'medium'}
      >
        <ToggleButton value="line">
          <ShowChart sx={{ mr: 1 }} />
          {!isMobile && 'Line'}
        </ToggleButton>
        <ToggleButton value="area">
          <AreaChartIcon sx={{ mr: 1 }} />
          {!isMobile && 'Area'}
        </ToggleButton>
      </ToggleButtonGroup>

      <FormControl size="small" sx={{ minWidth: 120 }}>
        <InputLabel>Time Range</InputLabel>
        <Select
          value={timeRange}
          label="Time Range"
          onChange={(e) => setTimeRange(e.target.value as TimeRange)}
        >
          <MenuItem value="3years">Last 3 Years</MenuItem>
          <MenuItem value="5years">Last 5 Years</MenuItem>
          <MenuItem value="all">All Years</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );

  const renderGrowthMetrics = () => {
    const incomeGrowth = getGrowthRate('gross_income');
    const taxGrowth = getGrowthRate('total_tax');
    const deductionsGrowth = getGrowthRate('deductions');
    
    return (
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)',
        gap: 2,
        mt: 3
      }}>
        <Card variant={incomeGrowth >= 0 ? 'success' : 'error'}>
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" fontWeight="bold">
              {formatPercentage(incomeGrowth)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Income Growth
            </Typography>
          </Box>
        </Card>
        
        <Card variant={taxGrowth <= incomeGrowth ? 'success' : 'warning'}>
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" fontWeight="bold">
              {formatPercentage(taxGrowth)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tax Growth
            </Typography>
          </Box>
        </Card>
        
        <Card variant={deductionsGrowth >= 0 ? 'success' : 'error'}>
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" fontWeight="bold">
              {formatPercentage(deductionsGrowth)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Deductions Growth
            </Typography>
          </Box>
        </Card>
      </Box>
    );
  };

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  if (!data || data.length === 0) {
    return (
      <Card variant="info">
        <Box sx={{ textAlign: 'center', p: 3 }}>
          <DateRange sx={{ fontSize: 60, color: 'info.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Historical Data Available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Complete a few tax calculations to see trends over time
          </Typography>
        </Box>
      </Card>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        {title}
      </Typography>
      
      <Card>
        {renderControls()}
        <Box sx={{ height: height }}>
          {chartType === 'line' ? renderLineChart() : renderAreaChart()}
        </Box>
      </Card>
      
      {renderGrowthMetrics()}
    </Box>
  );
};

export default TaxTrendsChart; 