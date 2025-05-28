import React from 'react';
import { Box, SxProps, Theme } from '@mui/material';

// Define interfaces
interface StatusColors {
  [key: string]: string;
  approved: string;
  pending: string;
  rejected: string;
  active: string;
  inactive: string;
  default: string;
}

interface StatusBadgeProps {
  status: string;
  statusColors?: StatusColors;
  sx?: SxProps<Theme>;
}

/**
 * Reusable status badge component with Material-UI styling
 */
const StatusBadge: React.FC<StatusBadgeProps> = ({ 
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
  const getStatusColor = (statusText: string): string => {
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

export default StatusBadge; 