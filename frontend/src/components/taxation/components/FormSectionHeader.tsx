import React from 'react';
import { Box, Typography, Divider, SxProps, Theme } from '@mui/material';

interface FormSectionHeaderProps {
  title: string;
  withDivider?: boolean;
  sx?: SxProps<Theme>;
}

/**
 * Reusable component for form section headers
 */
const FormSectionHeader: React.FC<FormSectionHeaderProps> = ({ 
  title, 
  withDivider = true, 
  sx = {} 
}) => {
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