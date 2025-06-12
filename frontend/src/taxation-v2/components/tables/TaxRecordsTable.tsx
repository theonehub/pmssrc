import React from 'react';
import { Box, Typography } from '@mui/material';

export interface TaxRecordsTableProps {
  data?: any[];
  loading?: boolean;
}

export const TaxRecordsTable: React.FC<TaxRecordsTableProps> = () => {
  return (
    <Box>
      <Typography variant="h6">Tax Records Table</Typography>
      <Typography variant="body2" color="text.secondary">
        Coming soon...
      </Typography>
    </Box>
  );
}; 