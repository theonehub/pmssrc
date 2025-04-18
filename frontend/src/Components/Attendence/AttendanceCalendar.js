import React, { useState, useEffect } from 'react';
import axios from '../../utils/axios';
import { Modal, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { BsChevronLeft, BsChevronRight } from 'react-icons/bs';

function AttendanceCalendar({ empId, show, onHide }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (show && empId) {
      fetchAttendanceData();
    }
  }, [show, empId, currentDate]);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();
      const response = await axios.get(`/attendance/user/${empId}/${month}/${year}`);
      setAttendanceData(response.data);
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

  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const renderTooltip = (date) => {
    const attendance = getAttendanceStatus(date);
    
    return (
      <Tooltip id={`tooltip-${date?.getDate() || 'empty'}`}>
        <div className="text-start">
          {attendance ? (
            <>
              <div><strong>Check-in:</strong> {formatTime(attendance.checkin_time)}</div>
              <div><strong>Check-out:</strong> {formatTime(attendance.checkout_time)}</div>
            </>
          ) : (
            <div>No attendance record</div>
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
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Attendance Calendar - {empId}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
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
              const attendance = getAttendanceStatus(date);
              const status = date ? (attendance ? 'present' : 'lwp') : 'empty';
              
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
    </Modal>
  );
}

export default AttendanceCalendar; 