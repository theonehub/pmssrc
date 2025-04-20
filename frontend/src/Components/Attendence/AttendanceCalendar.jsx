import React, { useState, useEffect, useRef } from 'react';
import axios from '../../utils/axios';
import { Modal, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { BsChevronLeft, BsChevronRight } from 'react-icons/bs';
import './AttendanceCalendar.css';

function AttendanceCalendar({ empId, show, onHide }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [attendanceData, setAttendanceData] = useState([]);
  const [holidays, setHolidays] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalSize, setModalSize] = useState('lg');
  const modalRef = useRef(null);

  useEffect(() => {
    if (show && empId) {
      fetchAttendanceData();
    }

    // Responsive modal size based on screen width
    const handleResize = () => {
      if (window.innerWidth < 576) {
        setModalSize('sm');
      } else if (window.innerWidth < 992) {
        setModalSize('md');
      } else {
        setModalSize('lg');
      }
    };

    handleResize(); // Set initial size
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [show, empId, currentDate]);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();
      const response = await axios.get(`/attendance/user/${empId}/${month}/${year}`);
      setAttendanceData(response.data);
      const holidayResponse = await axios.get(`/public-holidays/month/${month}/${year}`);
      setHolidays(holidayResponse.data);
      const leaveResponse = await axios.get(`/leaves/user/${empId}/${month}/${year}`);
      setLeaves(leaveResponse.data);
      console.log('Leaves:', leaveResponse.data);
    } catch (error) {
      console.error('Error fetching attendance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days = [];
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

  const getAttendanceStatus = (date) => {
    if (!date) return null;
    const attendance = attendanceData.find(
      (a) => 
        new Date(a.checkin_time).getDate() === date.getDate() &&
        new Date(a.checkin_time).getMonth() === date.getMonth() &&
        new Date(a.checkin_time).getFullYear() === date.getFullYear()
    );
    return attendance;
  };

  const getLeaveStatus = (date) => {
    if (!date) return null;
    return leaves.find(leave => {
      const startDate = new Date(leave.start_date);
      const endDate = new Date(leave.end_date);
      return date >= startDate && date <= endDate;
    });
  };

  const isPublicHoliday = (date) => {
    if (!date) return false;
    
    return holidays.some(holiday => {
      const holidayDate = new Date(holiday.date);
      return holidayDate.getDate() === date.getDate() &&
             holidayDate.getMonth() === date.getMonth() &&
             holidayDate.getFullYear() === date.getFullYear();
    });
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const renderTooltip = (date) => {
    if (!date) return <Tooltip id="tooltip-empty">No data</Tooltip>;
    
    const attendance = getAttendanceStatus(date);
    const holiday = holidays.find(h => {
      const holidayDate = new Date(h.date);
      return holidayDate.getDate() === date.getDate() &&
             holidayDate.getMonth() === date.getMonth() &&
             holidayDate.getFullYear() === date.getFullYear();
    });
    const leave = getLeaveStatus(date);
    
    return (
      <Tooltip id={`tooltip-${date.getDate()}`}>
        <div className="text-start">
          {holiday ? (
            <div><strong>Holiday:</strong> {holiday.name}</div>
          ) : leave ? (
            <div><strong>Leave:</strong> {leave.status}</div>
          ) : attendance ? (
            <>
              <div><strong>Check-in:</strong> {formatTime(attendance.checkin_time)}</div>
              <div><strong>Check-out:</strong> {formatTime(attendance.checkout_time)}</div>
            </>
          ) : (
            <div>Absent</div>
          )}
        </div>
      </Tooltip>
    );
  };

  const changeMonth = (increment) => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + increment, 1));
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  return (
    <Modal 
      show={show} 
      onHide={onHide} 
      size={modalSize}
      dialogClassName="attendance-calendar-modal"
      centered
      ref={modalRef}
    >
      <Modal.Header closeButton>
        <Modal.Title>Attendance Calendar - {empId}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="px-2 py-3">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <Button variant="outline-primary" onClick={() => changeMonth(-1)}>
            <BsChevronLeft />
          </Button>
          <h4 className="mb-0">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h4>
          <Button variant="outline-primary" onClick={() => changeMonth(1)}>
            <BsChevronRight />
          </Button>
        </div>

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
              let status = 'empty';
              console.log('Date:', date);
              if (date) {
                if (isPublicHoliday(date)) {
                  console.log('Public Holiday:', date);
                  status = 'public_holiday';
                } else {
                  const attendance = getAttendanceStatus(date);
                  const leave = getLeaveStatus(date);
                  if (leave) {
                    status = leave.status.toLowerCase();
                    console.log('Leave:', leave);
                  } else {
                    status = attendance ? 'present' : 'absent';
                  }
                }
              }
              
              return (
                <OverlayTrigger
                  key={index}
                  placement="top"
                  overlay={renderTooltip(date)}
                  delay={{ show: 250, hide: 400 }}
                >
                  <div
                    className={`calendar-cell ${status}`}
                  >
                    {date ? date.getDate() : ''}
                  </div>
                </OverlayTrigger>
              );
            })}
          </div>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>Close</Button>
      </Modal.Footer>
    </Modal>
  );
}

export default AttendanceCalendar; 