import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  SelectChangeEvent
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  FlightTakeoff as FlightTakeoffIcon,
  Receipt as ReceiptIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  GetApp as GetAppIcon
} from '@mui/icons-material';
import reportingService from '../../shared/api/reportingService';
import type { 
  ConsolidatedAnalytics, 
  ReimbursementAnalytics, 
  ExportRequest, 
  ExportResponse 
} from '../../shared/api/reportingService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reporting-tabpanel-${index}`}
      aria-labelledby={`reporting-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ReportingDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [dateRange] = useState({ start: '', end: '' });
  const [filterPeriod, setFilterPeriod] = useState<string>('current_month');

  // Calculate date range based on filter period
  const getDateRange = () => {
    const now = new Date();
    let startDate: string | undefined;
    let endDate: string | undefined;

    switch (filterPeriod) {
      case 'current_month':
        startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];
        break;
      case 'last_month':
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1).toISOString().split('T')[0];
        endDate = new Date(now.getFullYear(), now.getMonth(), 0).toISOString().split('T')[0];
        break;
      case 'current_quarter':
        const quarter = Math.floor(now.getMonth() / 3);
        startDate = new Date(now.getFullYear(), quarter * 3, 1).toISOString().split('T')[0];
        endDate = new Date(now.getFullYear(), (quarter + 1) * 3, 0).toISOString().split('T')[0];
        break;
      case 'current_year':
        startDate = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
        endDate = new Date(now.getFullYear(), 11, 31).toISOString().split('T')[0];
        break;
      case 'custom':
        startDate = dateRange.start || undefined;
        endDate = dateRange.end || undefined;
        break;
    }

    return { startDate, endDate };
  };

  const { startDate, endDate } = getDateRange();

  // React Query for consolidated data (v5 compatible)
  const {
    data: consolidatedData,
    isLoading: consolidatedLoading,
    error: consolidatedError,
    refetch: refetchConsolidated
  } = useQuery<ConsolidatedAnalytics, Error>({
    queryKey: ['consolidatedAnalytics', startDate, endDate],
    queryFn: async () => {
      console.log('Fetching consolidated analytics with dates:', { startDate, endDate });
      return reportingService.getConsolidatedAnalytics(startDate, endDate);
    },
    retry: 1,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (gcTime is the new cacheTime in v5)
  });

  // React Query for reimbursement data (v5 compatible)
  const {
    data: reimbursementData,
    isLoading: reimbursementLoading,
    error: reimbursementError,
    refetch: refetchReimbursement
  } = useQuery<ReimbursementAnalytics, Error>({
    queryKey: ['reimbursementAnalytics', startDate, endDate],
    queryFn: async () => {
      console.log('Fetching reimbursement analytics with dates:', { startDate, endDate });
      return reportingService.getReimbursementAnalytics(startDate, endDate);
    },
    retry: 1,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (gcTime is the new cacheTime in v5)
  });

  const loading = consolidatedLoading || reimbursementLoading;
  const error = consolidatedError || reimbursementError;

  // Debug logging
  React.useEffect(() => {
    console.log('ReportingDashboard state:', {
      tabValue,
      filterPeriod,
      dateRange,
      consolidatedData,
      reimbursementData,
      loading,
      error: error?.toString()
    });
  }, [tabValue, filterPeriod, dateRange, consolidatedData, reimbursementData, loading, error]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handlePeriodChange = (event: SelectChangeEvent<string>) => {
    setFilterPeriod(event.target.value);
  };

  const handleRefresh = () => {
    console.log('Manually refreshing data...');
    refetchConsolidated();
    refetchReimbursement();
  };

  const handleExport = async (format: 'pdf' | 'excel' | 'csv', reportType: string) => {
    try {
      setExportLoading(true);
      const exportRequest: ExportRequest = {
        report_type: reportType,
        format,
        ...(dateRange.start && { start_date: dateRange.start }),
        ...(dateRange.end && { end_date: dateRange.end })
      };

      const response: ExportResponse = await reportingService.exportReport(exportRequest);
      
      // Download the file
      reportingService.downloadExportedReport(
        response.download_url,
        `${reportType}_report.${format}`
      );

      setExportDialogOpen(false);
    } catch (err) {
      console.error('Error exporting report:', err);
    } finally {
      setExportLoading(false);
    }
  };

  const renderOverviewTab = () => {
    if (!consolidatedData) {
      console.log('No consolidated data available for overview tab');
      return (
        <Alert severity="warning">
          No data available. Please check your connection and try again.
        </Alert>
      );
    }

    const { dashboard_analytics } = consolidatedData;
    console.log('Rendering overview with dashboard_analytics:', dashboard_analytics);

    return (
      <Grid container spacing={4}>

        {/* Attendance Module */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Typography variant="h5" gutterBottom sx={{ color: 'success.main', fontWeight: 'bold' }}>
            ⏰ Attendance Management
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ScheduleIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.checkin_count || 0}</Typography>
                  <Typography color="textSecondary">Today's Check-ins</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ScheduleIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.checkout_count || 0}</Typography>
                  <Typography color="textSecondary">Today's Check-outs</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AssessmentIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.total_departments || 0}</Typography>
                  <Typography color="textSecondary">Total Departments</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>


         {/* Payroll Management Module */}
         {consolidatedData?.payroll_analytics && (
          <>
            <Grid item xs={12} sx={{ mt: 2 }}>
              <Typography variant="h5" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                💰 Payroll Management
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <PeopleIcon color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{consolidatedData.payroll_analytics.total_payouts_current_month || 0}</Typography>
                      <Typography color="textSecondary">Employees on Payroll</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <AssessmentIcon color="success" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">₹{(consolidatedData.payroll_analytics.total_amount_current_month || 0).toLocaleString()}</Typography>
                      <Typography color="textSecondary">Monthly Payroll</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <ReceiptIcon color="info" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">₹{(consolidatedData.payroll_analytics.average_salary || 0).toLocaleString()}</Typography>
                      <Typography color="textSecondary">Average Salary</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <AssessmentIcon color="warning" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">₹{((consolidatedData.payroll_analytics.total_amount_current_month || 0) * 12).toLocaleString()}</Typography>
                      <Typography color="textSecondary">Annual Cost</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {/* Reimbursement Module */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Typography variant="h5" gutterBottom sx={{ color: 'warning.main', fontWeight: 'bold' }}>
            💰 Reimbursement Management
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ReceiptIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.pending_reimbursements || 0}</Typography>
                  <Typography color="textSecondary">Pending Requests</Typography>
                  {reimbursementData && (
                    <Typography variant="body2" color="warning.main">
                      ₹{(reimbursementData.total_pending_amount || 0).toLocaleString()}
                    </Typography>
                  )}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {reimbursementData && (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <ReceiptIcon color="success" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{reimbursementData.total_approved_reimbursements || 0}</Typography>
                      <Typography color="textSecondary">Approved Requests</Typography>
                      <Typography variant="body2" color="success.main">
                        ₹{(reimbursementData.total_approved_amount || 0).toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <AssessmentIcon color="info" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">
                        {(reimbursementData.total_pending_reimbursements || 0) + (reimbursementData.total_approved_reimbursements || 0)}
                      </Typography>
                      <Typography color="textSecondary">Total Requests</Typography>
                      <Typography variant="body2" color="info.main">
                        ₹{((reimbursementData.total_pending_amount || 0) + (reimbursementData.total_approved_amount || 0)).toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <ReceiptIcon color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">
                        {reimbursementData.total_pending_reimbursements && reimbursementData.total_approved_reimbursements 
                          ? Math.round(((reimbursementData.total_approved_reimbursements / (reimbursementData.total_pending_reimbursements + reimbursementData.total_approved_reimbursements)) * 100))
                          : 0}%
                      </Typography>
                      <Typography color="textSecondary">Approval Rate</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}


        {/* User Management Module */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
            👥 User Management
          </Typography>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PeopleIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.total_users || 0}</Typography>
                  <Typography color="textSecondary">Total Users</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PeopleIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.active_users || 0}</Typography>
                  <Typography color="textSecondary">Active Users</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PeopleIcon color="error" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.inactive_users || 0}</Typography>
                  <Typography color="textSecondary">Inactive Users</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PeopleIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.recent_joiners_count || 0}</Typography>
                  <Typography color="textSecondary">Recent Joiners</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>


        {/* Leave Management Module */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Typography variant="h5" gutterBottom sx={{ color: 'info.main', fontWeight: 'bold' }}>
            🏖️ Leave Management
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <FlightTakeoffIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h4">{dashboard_analytics?.pending_leaves || 0}</Typography>
                  <Typography color="textSecondary">Pending Leaves</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

       

        {/* Distribution Charts Section */}
        <Grid item xs={12} sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
            📊 Organization Distribution
          </Typography>
        </Grid>

        {/* Department Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Department Distribution</Typography>
              <Box>
                {Object.entries(dashboard_analytics?.department_distribution || {}).map(([dept, count]) => (
                  <Box key={dept} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                    <Typography variant="body1">{dept}</Typography>
                    <Chip label={String(count)} color="primary" />
                  </Box>
                ))}
                {Object.keys(dashboard_analytics?.department_distribution || {}).length === 0 && (
                  <Typography color="textSecondary">No department data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Role Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Role Distribution</Typography>
              <Box>
                {Object.entries(dashboard_analytics?.role_distribution || {}).map(([role, count]) => (
                  <Box key={role} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                    <Typography variant="body1">{role}</Typography>
                    <Chip label={String(count)} color="secondary" />
                  </Box>
                ))}
                {Object.keys(dashboard_analytics?.role_distribution || {}).length === 0 && (
                  <Typography color="textSecondary">No role data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderUserAnalyticsTab = () => {
    if (!consolidatedData) return null;

    const { user_analytics } = consolidatedData;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>User Summary</Typography>
              <Box display="flex" gap={4}>
                <Box>
                  <Typography variant="h4" color="primary">{user_analytics?.total_users || 0}</Typography>
                  <Typography color="textSecondary">Total Users</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" color="success.main">{user_analytics?.active_users || 0}</Typography>
                  <Typography color="textSecondary">Active</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" color="error.main">{user_analytics?.inactive_users || 0}</Typography>
                  <Typography color="textSecondary">Inactive</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Recent Joiners</Typography>
              {user_analytics?.recent_joiners && user_analytics.recent_joiners.length > 0 ? (
                <Box>
                  {user_analytics.recent_joiners.slice(0, 5).map((joiner: any, index: number) => (
                    <Box key={index} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                      <Box>
                        <Typography variant="body1">{joiner.name}</Typography>
                        <Typography variant="body2" color="textSecondary">{joiner.department}</Typography>
                      </Box>
                      <Typography variant="body2" color="primary">
                        {new Date(joiner.date_of_joining).toLocaleDateString()}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography color="textSecondary">No recent joiners</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderAttendanceAnalyticsTab = () => {
    if (!consolidatedData) return null;

    const { attendance_analytics } = consolidatedData;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Today's Check-ins</Typography>
              <Typography variant="h4" color="success.main">
                {attendance_analytics?.total_checkins_today || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Today's Check-outs</Typography>
              <Typography variant="h4" color="primary">
                {attendance_analytics?.total_checkouts_today || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Present Count</Typography>
              <Typography variant="h4" color="success.main">
                {attendance_analytics?.present_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Absent Count</Typography>
              <Typography variant="h4" color="error.main">
                {attendance_analytics?.absent_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderPayrollAnalyticsTab = () => {
    if (!consolidatedData?.payroll_analytics) {
      return (
        <Alert severity="info">
          No payroll data available for the selected period.
        </Alert>
      );
    }

    const payrollData = consolidatedData.payroll_analytics;

    return (
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total Employees</Typography>
              <Typography variant="h4" color="primary">
                {payrollData.total_payouts_current_month || 0}
              </Typography>
              <Typography color="textSecondary">
                Current month payouts
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total Payroll</Typography>
              <Typography variant="h4" color="success.main">
                ₹{(payrollData.total_amount_current_month || 0).toLocaleString()}
              </Typography>
              <Typography color="textSecondary">
                Gross monthly amount
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Average Salary</Typography>
              <Typography variant="h4" color="info.main">
                ₹{(payrollData.average_salary || 0).toLocaleString()}
              </Typography>
              <Typography color="textSecondary">
                Per employee
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total TDS</Typography>
              <Typography variant="h4" color="warning.main">
                ₹{(payrollData.total_tds_current_month || 0).toLocaleString()}
              </Typography>
              <Typography color="textSecondary">
                Tax deducted at source
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Department Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Department Salary Distribution</Typography>
              <Box>
                {Object.keys(payrollData.department_salary_distribution || {}).length > 0 ? (
                  Object.entries(payrollData.department_salary_distribution || {}).map(([dept, data]: [string, any]) => (
                    <Box key={dept} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                      <Box>
                        <Typography variant="body1">{dept}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {data.count || 0} employees
                        </Typography>
                      </Box>
                      <Box textAlign="right">
                        <Chip 
                          label={`₹${(data.average_gross || 0).toLocaleString()}`} 
                          color="primary" 
                          size="small" 
                        />
                        <Typography variant="body2" color="textSecondary">
                          Avg: ₹{(data.total_gross || 0).toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                  ))
                ) : (
                  <Typography color="textSecondary">No department data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Salary Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Monthly Salary Trends</Typography>
              <Box>
                {Object.keys(payrollData.salary_trends || {}).length > 0 ? (
                  Object.entries(payrollData.salary_trends || {}).map(([month, data]: [string, any]) => (
                    <Box key={month} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                      <Typography variant="body1">{month}</Typography>
                      <Box textAlign="right">
                        <Typography variant="body1">
                          {data.total_payouts || 0} payouts
                        </Typography>
                        <Typography variant="body2" color="primary">
                          ₹{(data.total_amount || 0).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Avg: ₹{(data.average_salary || 0).toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                  ))
                ) : (
                  <Typography color="textSecondary">No trend data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* TDS Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>TDS Trends</Typography>
              <Box>
                {Object.keys(payrollData.tds_trends || {}).length > 0 ? (
                  Object.entries(payrollData.tds_trends || {}).map(([month, data]: [string, any]) => (
                    <Box key={month} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                      <Typography variant="body1">{month}</Typography>
                      <Box textAlign="right">
                        <Typography variant="body1" color="warning.main">
                          ₹{(data.total_tds || 0).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Avg: ₹{(data.average_tds || 0).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="info.main">
                          {data.tds_percentage || 0}% of gross
                        </Typography>
                      </Box>
                    </Box>
                  ))
                ) : (
                  <Typography color="textSecondary">No TDS trend data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Department TDS Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Department TDS Distribution</Typography>
              <Box>
                {Object.keys(payrollData.department_tds_distribution || {}).length > 0 ? (
                  Object.entries(payrollData.department_tds_distribution || {}).map(([dept, data]: [string, any]) => (
                    <Box key={dept} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                      <Box>
                        <Typography variant="body1">{dept}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {data.count || 0} employees
                        </Typography>
                      </Box>
                      <Box textAlign="right">
                        <Chip 
                          label={`₹${(data.average_tds || 0).toLocaleString()}`} 
                          color="warning" 
                          size="small" 
                        />
                        <Typography variant="body2" color="textSecondary">
                          Total: ₹{(data.total_tds || 0).toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                  ))
                ) : (
                  <Typography color="textSecondary">No department TDS data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Payroll Breakdown */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Payroll Components Analysis</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" color="primary">Gross Pay</Typography>
                      <Typography variant="h5">
                        ₹{(payrollData.total_amount_current_month || 0).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        100% of total payroll
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" color="warning.main">TDS Deducted</Typography>
                      <Typography variant="h5">
                        ₹{(payrollData.total_tds_current_month || 0).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Avg: ₹{(payrollData.average_tds_per_employee || 0).toLocaleString()} per employee
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" color="info.main">Estimated EPF</Typography>
                      <Typography variant="h5">
                        ₹{((payrollData.total_amount_current_month || 0) * 0.12).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        ~12% of basic pay
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" color="success.main">Estimated Net Pay</Typography>
                      <Typography variant="h5">
                        ₹{((payrollData.total_amount_current_month || 0) - (payrollData.total_tds_current_month || 0) - ((payrollData.total_amount_current_month || 0) * 0.12)).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        After TDS & EPF deductions
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Payroll Actions</Typography>
              <Box display="flex" gap={2}>
                <Button 
                  variant="outlined" 
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport('excel', 'payroll')}
                >
                  Export Payroll Report
                </Button>
                <Button 
                  variant="outlined" 
                  startIcon={<GetAppIcon />}
                  onClick={() => handleExport('csv', 'payroll')}
                >
                  Export CSV
                </Button>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => {
                    // Navigate to payroll management
                    window.location.href = '/admin-payouts';
                  }}
                >
                  Manage Payroll
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderReimbursementAnalyticsTab = () => {
    if (!reimbursementData) {
      return (
        <Alert severity="info">
          No reimbursement data available for the selected period.
        </Alert>
      );
    }

    return (
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Pending Reimbursements</Typography>
              <Typography variant="h4" color="warning.main">
                {reimbursementData.total_pending_reimbursements || 0}
              </Typography>
              <Typography color="textSecondary">
                Amount: ₹{(reimbursementData.total_pending_amount || 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Approved Reimbursements</Typography>
              <Typography variant="h4" color="success.main">
                {reimbursementData.total_approved_reimbursements || 0}
              </Typography>
              <Typography color="textSecondary">
                Amount: ₹{(reimbursementData.total_approved_amount || 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total Requests</Typography>
              <Typography variant="h4" color="primary">
                {(reimbursementData.total_pending_reimbursements || 0) + (reimbursementData.total_approved_reimbursements || 0)}
              </Typography>
              <Typography color="textSecondary">
                All time
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total Amount</Typography>
              <Typography variant="h4" color="info.main">
                ₹{((reimbursementData.total_pending_amount || 0) + (reimbursementData.total_approved_amount || 0)).toLocaleString()}
              </Typography>
              <Typography color="textSecondary">
                All requests
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Status Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Status Distribution</Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography>Pending</Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip 
                      label={reimbursementData.total_pending_reimbursements || 0} 
                      color="warning" 
                      size="small" 
                    />
                    <Typography variant="body2" color="textSecondary">
                      ₹{(reimbursementData.total_pending_amount || 0).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography>Approved</Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip 
                      label={reimbursementData.total_approved_reimbursements || 0} 
                      color="success" 
                      size="small" 
                    />
                    <Typography variant="body2" color="textSecondary">
                      ₹{(reimbursementData.total_approved_amount || 0).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Type Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Type Distribution</Typography>
              <Box>
                {Object.keys(reimbursementData.reimbursement_type_distribution || {}).length > 0 ? (
                  Object.entries(reimbursementData.reimbursement_type_distribution || {}).map(([type, data]: [string, any]) => (
                    <Box key={type} display="flex" justifyContent="space-between" alignItems="center" py={1}>
                      <Typography variant="body1">{type}</Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip 
                          label={String(typeof data === 'object' ? data.count : data)} 
                          color="primary" 
                          size="small" 
                        />
                        {typeof data === 'object' && data.amount && (
                          <Typography variant="body2" color="textSecondary">
                            ₹{data.amount.toLocaleString()}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  ))
                ) : (
                  <Typography color="textSecondary">No type distribution data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Monthly Trends */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Monthly Trends</Typography>
              <Box>
                {Object.keys(reimbursementData.monthly_reimbursement_trends || {}).length > 0 ? (
                  <Grid container spacing={2}>
                    {Object.entries(reimbursementData.monthly_reimbursement_trends || {}).map(([month, data]: [string, any]) => (
                      <Grid item xs={12} sm={6} md={4} key={month}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="h6">{month}</Typography>
                            {typeof data === 'object' && data.pending && data.approved ? (
                              <>
                                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                  <Typography variant="body2">Pending:</Typography>
                                  <Chip 
                                    label={`${data.pending.count} (₹${data.pending.amount.toLocaleString()})`} 
                                    color="warning" 
                                    size="small" 
                                  />
                                </Box>
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                  <Typography variant="body2">Approved:</Typography>
                                  <Chip 
                                    label={`${data.approved.count} (₹${data.approved.amount.toLocaleString()})`} 
                                    color="success" 
                                    size="small" 
                                  />
                                </Box>
                              </>
                            ) : (
                              <>
                                <Typography variant="body1">
                                  Requests: {String(typeof data === 'object' ? data.count : data)}
                                </Typography>
                                {typeof data === 'object' && data.amount && (
                                  <Typography variant="body2" color="primary">
                                    Amount: ₹{data.amount.toLocaleString()}
                                  </Typography>
                                )}
                              </>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography color="textSecondary">No monthly trends data available</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Quick Actions</Typography>
              <Box display="flex" gap={2}>
                <Button 
                  variant="outlined" 
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport('excel', 'reimbursement')}
                >
                  Export to Excel
                </Button>
                <Button 
                  variant="outlined" 
                  startIcon={<GetAppIcon />}
                  onClick={() => handleExport('csv', 'reimbursement')}
                >
                  Export to CSV
                </Button>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => {
                    // Navigate to reimbursement approvals
                    window.location.href = '/reimbursement-approvals';
                  }}
                >
                  Go to Approvals
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={handleRefresh}>
          Retry
        </Button>
      }>
        Error loading reporting data: {error.message}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Reporting & Analytics
      </Typography>

      {/* Controls */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <FormControl variant="outlined" size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Time Period</InputLabel>
          <Select
            value={filterPeriod}
            onChange={handlePeriodChange}
            label="Time Period"
          >
            <MenuItem value="current_month">Current Month</MenuItem>
            <MenuItem value="last_month">Last Month</MenuItem>
            <MenuItem value="current_quarter">Current Quarter</MenuItem>
            <MenuItem value="current_year">Current Year</MenuItem>
            <MenuItem value="custom">Custom Range</MenuItem>
          </Select>
        </FormControl>

        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => setExportDialogOpen(true)}
          >
            Export
          </Button>
        </Box>
      </Box>

      {/* Main Content Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="reporting tabs">
          <Tab label="Overview" />
          <Tab label="Users" />
          <Tab label="Attendance" />
          <Tab label="Leaves" />
          <Tab label="Payroll" />
          <Tab label="Reimbursements" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {renderOverviewTab()}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {renderUserAnalyticsTab()}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {renderAttendanceAnalyticsTab()}
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography variant="h6">Leave Analytics</Typography>
        <Alert severity="info">Leave analytics coming soon...</Alert>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        {renderPayrollAnalyticsTab()}
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        {renderReimbursementAnalyticsTab()}
      </TabPanel>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)}>
        <DialogTitle>Export Reports</DialogTitle>
        <DialogContent>
          <Typography>Choose export format:</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => handleExport('pdf', 'dashboard')} disabled={exportLoading}>
            PDF
          </Button>
          <Button onClick={() => handleExport('excel', 'dashboard')} disabled={exportLoading}>
            Excel
          </Button>
          <Button onClick={() => handleExport('csv', 'dashboard')} disabled={exportLoading}>
            CSV
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ReportingDashboard; 
