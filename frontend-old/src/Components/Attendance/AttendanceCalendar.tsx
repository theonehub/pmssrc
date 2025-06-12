import React, { useState, useEffect, useCallback } from 'react';
import axios from '../../utils/axios';
import './AttendanceCalendar.css';
import {
  Modal,
  Box,
  Button,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  SxProps,
  Theme
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

// Define types for the component
interface AttendanceRecord {
  checkin_time: string;
  checkout_time?: string;
}

interface Holiday {
  date: string;
  name: string;
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
  const [attendanceData, setAttendanceData] = useState<AttendanceRecord[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [leaves, setLeaves] = useState<LeaveRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchAttendanceData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();
      
      // Use the legacy endpoints that match the expected data format
      const response = await axios.get<AttendanceRecord[]>(`/api/v2/attendance/user/${employee_id}/${month}/${year}`);
      setAttendanceData(response.data);
      
      const holidayResponse = await axios.get<Holiday[]>(`/api/v2/public-holidays/month/${month}/${year}`);
      setHolidays(holidayResponse.data);
      
      const leaveResponse = await axios.get<LeaveRecord[]>(`/api/v2/employee-leave/user/${employee_id}/${month}/${year}`);
      setLeaves(leaveResponse.data);
      
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log('Leaves:', leaveResponse.data);
      }
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching attendance data:', error);
      }
    } finally {
      setLoading(false);
    }
  }, [employee_id, currentDate]);

  useEffect(() => {
    if (show && employee_id) {
      fetchAttendanceData();
    }
  }, [show, employee_id, fetchAttendanceData]);

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
    const attendance = attendanceData.find(
      (a) => 
        new Date(a.checkin_time).getDate() === date.getDate() &&
        new Date(a.checkin_time).getMonth() === date.getMonth() &&
        new Date(a.checkin_time).getFullYear() === date.getFullYear()
    );
    return attendance || null;
  };

  const getLeaveStatus = (date: Date | null): LeaveRecord | null => {
    if (!date) return null;
    
    // Find any leave that includes this date
    return leaves.find(leave => {
      const startDate = new Date(leave.start_date);
      const endDate = new Date(leave.end_date);
      
      // Check if the date is within the leave period (inclusive)
      return date >= startDate && date <= endDate;
    }) || null;
  };

  const isPublicHoliday = (date: Date | null): boolean => {
    if (!date) return false;
    
    return holidays.some(holiday => {
      const holidayDate = new Date(holiday.date);
      return holidayDate.getDate() === date.getDate() &&
             holidayDate.getMonth() === date.getMonth() &&
             holidayDate.getFullYear() === date.getFullYear();
    });
  };

  const formatTime = (dateString?: string): string => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const renderTooltipContent = (date: Date | null): React.ReactElement | string => {
    if (!date) return "No data";
    
    const attendance = getAttendanceStatus(date);
    const holiday = holidays.find(h => {
      const holidayDate = new Date(h.date);
      return holidayDate.getDate() === date.getDate() &&
             holidayDate.getMonth() === date.getMonth() &&
             holidayDate.getFullYear() === date.getFullYear();
    });
    const leave = getLeaveStatus(date);
    
    if (holiday) {
      return (
        <Typography>
          <strong>Holiday:</strong> {holiday.name}
        </Typography>
      );
    }
    
    if (leave) {
      return (
        <>
          <Typography><strong>Leave:</strong> {leave.leave_name}</Typography>
          <Typography><strong>Status:</strong> {leave.status}</Typography>
          <Typography><strong>Duration:</strong> {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()}</Typography>
          <Typography><strong>Working Days:</strong> {leave.leave_count}</Typography>
          {leave.days_in_month && <Typography><strong>Days in current month:</strong> {leave.days_in_month}</Typography>}
          <Typography><strong>Reason:</strong> {leave.reason || 'Not specified'}</Typography>
        </>
      );
    }
    
    if (attendance) {
      return (
        <>
          <Typography><strong>Check-in:</strong> {formatTime(attendance.checkin_time)}</Typography>
          <Typography><strong>Check-out:</strong> {formatTime(attendance.checkout_time)}</Typography>
        </>
      );
    }
    
    return "Absent";
  };

  const changeMonth = (increment: number): void => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + increment, 1));
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  const modalStyle: SxProps<Theme> = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: {
      xs: '95%',
      sm: '85%',
      md: '75%',
      lg: '70%'
    },
    maxWidth: '1000px',
    maxHeight: {
      xs: '95vh',
      sm: '90vh',
      md: '85vh'
    },
    bgcolor: 'background.paper',
    boxShadow: 24,
    borderRadius: 2,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column'
  };

  const headerStyle: SxProps<Theme> = {
    px: 2,
    py: 1.5,
    borderBottom: 1,
    borderColor: 'divider'
  };

  const contentStyle: SxProps<Theme> = {
    p: {
      xs: 1,
      sm: 1.5,
      md: 2
    },
    flex: 1,
    overflow: 'auto'
  };

  const footerStyle: SxProps<Theme> = {
    p: 2,
    borderTop: 1,
    borderColor: 'divider',
    display: 'flex',
    justifyContent: 'flex-end'
  };

  return (
    <Modal
      open={show}
      onClose={onHide}
      aria-labelledby="attendance-calendar-modal"
      sx={{
        zIndex: (theme: Theme) => theme.zIndex.drawer + 2
      }}
    >
      <Box sx={modalStyle}>
        {/* Header */}
        <Box sx={headerStyle}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography 
              variant="h6" 
              component="h2"
              sx={{ 
                fontSize: { 
                  xs: '1rem',
                  sm: '1.1rem',
                  md: '1.25rem' 
                } 
              }}
            >
              Attendance Calendar - {employee_id}
            </Typography>
            <IconButton onClick={onHide} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5 }}>
            <IconButton onClick={() => changeMonth(-1)} size="small">
              <ChevronLeftIcon />
            </IconButton>
            <Typography 
              variant="h6" 
              sx={{ 
                fontSize: { 
                  xs: '0.9rem',
                  sm: '1rem',
                  md: '1.1rem' 
                } 
              }}
            >
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </Typography>
            <IconButton onClick={() => changeMonth(1)} size="small">
              <ChevronRightIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Content */}
        <Box sx={contentStyle}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: { xs: 0.5, sm: 1, md: 1.5 },
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {loading ? (
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '200px' 
              }}>
                <Typography>Loading attendance data...</Typography>
              </Box>
            ) : (
              <div className="calendar-grid">
                <div className="calendar-header">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                    <div key={day} className="calendar-cell header-cell">
                      {day}
                    </div>
                  ))}
                </div>
                <div className="calendar-body">
                  {days.map((date, index) => {
                    let status: AttendanceStatus = 'empty';
                    if (date) {
                      if (isPublicHoliday(date)) {
                        status = 'public_holiday';
                      } else {
                        const attendance = getAttendanceStatus(date);
                        const leave = getLeaveStatus(date);
                        if (leave) {
                          status = leave.status.toLowerCase() as AttendanceStatus;
                        } else {
                          status = attendance ? 'present' : 'absent';
                        }
                      }
                    }
                    
                    return (
                      <Tooltip
                        key={index}
                        title={
                          <Box>
                            {renderTooltipContent(date)}
                          </Box>
                        }
                        arrow
                        placement="top"
                      >
                        <div className={`calendar-cell ${status}`}>
                          {date ? date.getDate() : ''}
                        </div>
                      </Tooltip>
                    );
                  })}
                </div>
              </div>
            )}
          </Paper>
        </Box>

        {/* Footer */}
        <Box sx={footerStyle}>
          <Button 
            variant="contained" 
            onClick={onHide}
            size="small"
          >
            Close
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default AttendanceCalendar; 