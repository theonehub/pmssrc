import React, { useState } from 'react';
import { useAttendanceQuery } from '../../shared/hooks/useAttendance';
import {
  Modal,
  Box,
  Button,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  SxProps,
  Theme,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Divider,
  Avatar,
  Stack
} from '@mui/material';
import {
  Close as CloseIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Event as EventIcon,
  AccessTime as AccessTimeIcon,
  CalendarMonth as CalendarMonthIcon
} from '@mui/icons-material';

// Define types for the component
interface AttendanceRecord {
  attendance_id: string;
  employee_id: string;
  attendance_date: string;
  status: {
    status: string;
    marking_type: string;
    is_regularized: boolean;
    regularization_reason: string | null;
  };
  working_hours: {
    check_in_time: string;
    check_out_time: string;
    total_hours: number;
    break_hours: number;
    overtime_hours: number;
    shortage_hours: number;
    expected_hours: number;
    is_complete_day: boolean;
    is_full_day: boolean;
    is_half_day: boolean;
  };
  check_in_location: string | null;
  check_out_location: string | null;
  comments: string | null;
  admin_notes: string | null;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
}

interface LeaveRecord {
  leave_name: string;
  status: string;
  start_date: string;
  end_date: string;
  leave_count: number;
  days_in_month?: number;
  reason?: string;
}

interface AttendanceCalendarProps {
  employee_id: string;
  show: boolean;
  onHide: () => void;
}

type AttendanceStatus = 'empty' | 'present' | 'absent' | 'public_holiday' | 'approved' | 'pending' | 'rejected';

const AttendanceCalendar: React.FC<AttendanceCalendarProps> = ({ employee_id, show, onHide }) => {
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const { data: attendanceData, isLoading } = useAttendanceQuery({ 
    employee_id, 
    month: currentDate.getMonth() + 1, 
    year: currentDate.getFullYear() 
  });

  // --- Public Holidays State and Fetch ---
  const [publicHolidays, setPublicHolidays] = useState<{ date: string, name: string }[]>([]);
  React.useEffect(() => {
    const fetchHolidays = async () => {
      try {
        const month = currentDate.getMonth() + 1;
        const year = currentDate.getFullYear();
        const res = await fetch(`/v2/public-holidays/month/${month}/${year}`);
        const data = await res.json();
        setPublicHolidays(data || []);
      } catch (e) {
        setPublicHolidays([]);
      }
    };
    fetchHolidays();
  }, [currentDate]);

  // Debug logging
  React.useEffect(() => {
    if (attendanceData) {
      console.log('AttendanceCalendar - Raw attendance data:', attendanceData);
    }
  }, [attendanceData]);

  const getDaysInMonth = (date: Date): (Date | null)[] => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days: (Date | null)[] = [];
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }

    return days;
  };

  const getAttendanceStatus = (date: Date | null): AttendanceRecord | null => {
    if (!date) return null;
    const records = Array.isArray(attendanceData) ? attendanceData : (attendanceData?.data || []);
    
    const attendance = records.find(
      (a: any) => {
        const attendanceDate = new Date(a.attendance_date);
        return attendanceDate.getDate() === date.getDate() &&
               attendanceDate.getMonth() === date.getMonth() &&
               attendanceDate.getFullYear() === date.getFullYear();
      }
    );
    
    return attendance || null;
  };

  const getLeaveStatus = (date: Date | null): LeaveRecord | null => {
    if (!date) return null;
    
    const records = Array.isArray(attendanceData) ? attendanceData : (attendanceData?.data || []);
    return records.find((leave: any) => {
      const startDate = new Date(leave.start_date);
      const endDate = new Date(leave.end_date);
      
      return date >= startDate && date <= endDate;
    }) || null;
  };

  const formatTime = (dateString?: string): string => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status: AttendanceStatus): string => {
    switch (status) {
      case 'present': return '#4caf50';
      case 'absent': return '#f44336';
      case 'pending': return '#ff9800';
      case 'approved': return '#2196f3';
      case 'rejected': return '#e91e63';
      case 'public_holiday': return '#9c27b0';
      default: return '#e0e0e0';
    }
  };

  const getStatusIcon = (status: AttendanceStatus) => {
    switch (status) {
      case 'present': return <CheckCircleIcon sx={{ fontSize: 16 }} />;
      case 'absent': return <CancelIcon sx={{ fontSize: 16 }} />;
      case 'public_holiday': return <EventIcon sx={{ fontSize: 16 }} />;
      default: return null;
    }
  };

  const renderDayCell = (date: Date | null, index: number) => {
    if (!date) {
      return (
        <Box
          key={index}
          sx={{
            aspectRatio: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 60,
            backgroundColor: 'transparent'
          }}
        />
      );
    }

    let status: AttendanceStatus = 'empty';
    const attendance = getAttendanceStatus(date);
    const leave = getLeaveStatus(date);
    const holiday = publicHolidays.find((h) => {
      const holidayDate = new Date(h.date);
      return (
        holidayDate.getDate() === date.getDate() &&
        holidayDate.getMonth() === date.getMonth() &&
        holidayDate.getFullYear() === date.getFullYear()
      );
    });
    const isHoliday = !!holiday;

    if (isHoliday) {
      status = 'public_holiday';
    } else if (leave) {
      status = leave.status.toLowerCase() as AttendanceStatus;
    } else if (attendance) {
      const attendanceStatus = attendance.status?.status?.toLowerCase();
      status = attendanceStatus === 'present' ? 'present' : attendanceStatus === 'absent' ? 'absent' : 'present';
    } else {
      status = 'absent';
    }

    const isToday = new Date().toDateString() === date.toDateString();
    const statusColor = getStatusColor(status);

    return (
      <Tooltip
        key={index}
        title={
          <Box sx={{ p: 1 }}>
            {isHoliday && (
              <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                🎉 Public Holiday{holiday?.name ? `: ${holiday.name}` : ''}
              </Typography>
            )}
            {leave && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  📅 {leave.leave_name}
                </Typography>
                <Typography variant="caption">Status: {leave.status}</Typography>
                <Typography variant="caption" display="block">
                  {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()}
                </Typography>
              </>
            )}
            {attendance && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  ⏰ Attendance Details
                </Typography>
                <Typography variant="caption" display="block">
                  Check-in: {formatTime(attendance.working_hours?.check_in_time)}
                </Typography>
                <Typography variant="caption" display="block">
                  Check-out: {formatTime(attendance.working_hours?.check_out_time)}
                </Typography>
                <Typography variant="caption" display="block">
                  Total Hours: {attendance.working_hours?.total_hours || 0}h
                </Typography>
                {attendance.working_hours?.shortage_hours > 0 && (
                  <Typography variant="caption" display="block" color="error">
                    Shortage: {attendance.working_hours.shortage_hours}h
                  </Typography>
                )}
              </>
            )}
            {!attendance && !leave && !isHoliday && (
              <Typography variant="body2" color="error">
                ❌ Absent
              </Typography>
            )}
          </Box>
        }
        arrow
        placement="top"
      >
        <Card
          sx={{
            aspectRatio: 1,
            minHeight: 60,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            border: isToday ? '2px solid #1976d2' : '1px solid #e0e0e0',
            backgroundColor: statusColor + '20',
            position: 'relative',
            '&:hover': {
              transform: 'scale(1.05)',
              boxShadow: 3,
              backgroundColor: statusColor + '40'
            }
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 4,
              right: 4,
              color: statusColor
            }}
          >
            {getStatusIcon(status)}
          </Box>
          
          <Typography
            variant="body1"
            sx={{
              fontWeight: isToday ? 'bold' : 'normal',
              color: isToday ? '#1976d2' : 'text.primary',
              fontSize: '1rem'
            }}
          >
            {date.getDate()}
          </Typography>
          
          {attendance?.working_hours?.total_hours && (
            <Typography
              variant="caption"
              sx={{
                color: statusColor,
                fontWeight: 'bold',
                fontSize: '0.7rem'
              }}
            >
              {attendance.working_hours.total_hours}h
            </Typography>
          )}
        </Card>
      </Tooltip>
    );
  };

  const changeMonth = (increment: number): void => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + increment, 1));
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  const modalStyle: SxProps<Theme> = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: {
      xs: '95%',
      sm: '90%',
      md: '85%',
      lg: '80%'
    },
    maxWidth: '1200px',
    maxHeight: {
      xs: '95vh',
      sm: '90vh',
      md: '85vh'
    },
    bgcolor: 'background.paper',
    boxShadow: 24,
    borderRadius: 3,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column'
  };

  // Calculate attendance statistics
  const records = Array.isArray(attendanceData) ? attendanceData : (attendanceData?.data || []);
  const presentDays = records.filter((r: any) => r.status?.status?.toLowerCase() === 'present').length;
  const absentDays = records.filter((r: any) => r.status?.status?.toLowerCase() === 'absent').length;
  const totalWorkingDays = presentDays + absentDays;

  return (
    <Modal
      open={show}
      onClose={onHide}
      aria-labelledby="attendance-calendar-modal"
      sx={{ zIndex: (theme: Theme) => theme.zIndex.drawer + 2 }}
    >
      <Box sx={modalStyle}>
        {/* Header */}
        <Box sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          p: 3
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                <CalendarMonthIcon />
              </Avatar>
              <Box>
                <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
                  Attendance Calendar
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Employee: {employee_id}
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={onHide} sx={{ color: 'white' }}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          {/* Month Navigation */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <IconButton onClick={() => changeMonth(-1)} sx={{ color: 'white' }}>
              <ChevronLeftIcon />
            </IconButton>
            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </Typography>
            <IconButton onClick={() => changeMonth(1)} sx={{ color: 'white' }}>
              <ChevronRightIcon />
            </IconButton>
          </Box>

          {/* Statistics */}
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(3, 1fr)', 
            gap: 2 
          }}>
            <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'white' }}>
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  {presentDays}
                </Typography>
                <Typography variant="caption">Present Days</Typography>
              </CardContent>
            </Card>
            <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'white' }}>
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  {absentDays}
                </Typography>
                <Typography variant="caption">Absent Days</Typography>
              </CardContent>
            </Card>
            <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'white' }}>
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  {totalWorkingDays > 0 ? Math.round((presentDays / totalWorkingDays) * 100) : 0}%
                </Typography>
                <Typography variant="caption">Attendance</Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Content */}
        <Box sx={{ p: 3, flex: 1, overflow: 'auto' }}>
          {isLoading ? (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '300px',
              flexDirection: 'column',
              gap: 2
            }}>
              <CircularProgress size={60} />
              <Typography variant="h6" color="text.secondary">
                Loading attendance data...
              </Typography>
            </Box>
          ) : (
            <>
              {/* Legend */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  Legend
                </Typography>
                <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                  <Chip
                    icon={<CheckCircleIcon />}
                    label="Present"
                    sx={{ bgcolor: '#4caf5020', color: '#4caf50', border: '1px solid #4caf50' }}
                  />
                  <Chip
                    icon={<CancelIcon />}
                    label="Absent"
                    sx={{ bgcolor: '#f4433620', color: '#f44336', border: '1px solid #f44336' }}
                  />
                  <Chip
                    icon={<EventIcon />}
                    label="Holiday"
                    sx={{ bgcolor: '#9c27b020', color: '#9c27b0', border: '1px solid #9c27b0' }}
                  />
                  <Chip
                    icon={<AccessTimeIcon />}
                    label="Leave"
                    sx={{ bgcolor: '#ff980020', color: '#ff9800', border: '1px solid #ff9800' }}
                  />
                </Stack>
              </Box>

              <Divider sx={{ mb: 3 }} />

              {/* Calendar Grid */}
              <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
                {/* Day Headers */}
                <Box sx={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(7, 1fr)', 
                  gap: 1, 
                  mb: 1 
                }}>
                  {dayNames.map((day) => (
                    <Box key={day} sx={{ display: 'flex', justifyContent: 'center' }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          fontWeight: 'bold',
                          color: 'primary.main',
                          textAlign: 'center',
                          p: 1
                        }}
                      >
                        {day.substring(0, 3)}
                      </Typography>
                    </Box>
                  ))}
                </Box>

                {/* Calendar Days */}
                <Box sx={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(7, 1fr)', 
                  gap: 1 
                }}>
                  {days.map((date, index) => (
                    <Box key={index} sx={{ display: 'flex', justifyContent: 'center' }}>
                      {renderDayCell(date, index)}
                    </Box>
                  ))}
                </Box>
              </Paper>
            </>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ 
          p: 2, 
          borderTop: 1, 
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'flex-end',
          bgcolor: 'grey.50'
        }}>
          <Button 
            variant="contained" 
            onClick={onHide}
            size="large"
            sx={{
              borderRadius: 2,
              px: 4
            }}
          >
            Close
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default AttendanceCalendar;