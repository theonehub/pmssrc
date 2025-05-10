import React from 'react';
import { Box, Typography, Divider } from '@mui/material';

/**
 * Reusable component for form section headers
 * @param {Object} props - Component props 
 * @param {string} props.title - Section title
 * @param {boolean} props.withDivider - Whether to include a divider
 * @param {Object} props.sx - Additional styling
 * @returns {JSX.Element} Form section header
 */
const FormSectionHeader = ({ title, withDivider = true, sx = {} }) => {
  return (
    <>
      {withDivider && <Divider sx={{ my: 3, width: '100%' }} />}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2,
          ...sx
        }}
      >
        <Typography variant="h6" color="primary">{title}</Typography>
      </Box>
    </>
  );
};

export default FormSectionHeader; 