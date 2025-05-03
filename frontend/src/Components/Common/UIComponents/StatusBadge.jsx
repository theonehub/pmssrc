import React from 'react';
import PropTypes from 'prop-types';
import { Box } from '@mui/material';

/**
 * Reusable status badge component with Material-UI styling
 * 
 * @param {Object} props - Component props
 * @param {string} props.status - Status text to display
 * @param {Object} props.statusColors - Map of status to color (optional)
 * @param {Object} props.sx - Additional styles for the badge
 */
const StatusBadge = ({ 
  status, 
  statusColors = {
    approved: 'success.main',
    pending: 'warning.main',
    rejected: 'error.main',
    active: 'success.main',
    inactive: 'error.main',
    default: 'grey.500'
  },
  sx = {} 
}) => {
  const getStatusColor = (statusText) => {
    const normalizedStatus = statusText?.toLowerCase() || '';
    return statusColors[normalizedStatus] || statusColors.default;
  };

  return (
    <Box
      component="span"
      sx={{
        display: 'inline-block',
        padding: '4px 8px',
        borderRadius: '4px',
        backgroundColor: getStatusColor(status),
        color: 'white',
        fontSize: '0.75rem',
        fontWeight: 'bold',
        textTransform: 'capitalize',
        ...sx
      }}
    >
      {status}
    </Box>
  );
};

StatusBadge.propTypes = {
  status: PropTypes.string.isRequired,
  statusColors: PropTypes.object,
  sx: PropTypes.object
};

export default StatusBadge; 