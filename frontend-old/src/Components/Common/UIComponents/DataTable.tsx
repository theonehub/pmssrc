import React, { ReactNode } from 'react';
import {
  Paper,
  Table,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Box,
  Typography,
  CircularProgress,
  Pagination
} from '@mui/material';

// Define interfaces
interface Column<T = any> {
  field: keyof T;
  headerName: string;
  renderCell?: (row: T) => ReactNode;
  width?: number | string;
}

interface DataTableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
  renderActions?: (row: T) => ReactNode;
  page?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  title?: string;
}

/**
 * Reusable data table component with Material-UI styling
 */
const DataTable = <T extends Record<string, any> = any>({
  columns,
  data,
  loading = false,
  emptyMessage = 'No data found',
  renderActions,
  page = 1,
  totalPages = 1,
  onPageChange,
  title
}: DataTableProps<T>): React.ReactElement => {
  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number): void => {
    if (onPageChange) {
      onPageChange(value);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {title && (
        <Typography variant="h6" sx={{ mb: 2 }}>
          {title}
        </Typography>
      )}
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ 
              '& .MuiTableCell-head': { 
                backgroundColor: 'primary.main',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '0.875rem',
                padding: '12px 16px'
              }
            }}>
              {columns.map((column) => (
                <TableCell 
                  key={String(column.field)} 
                  sx={{ width: column.width || 'auto' }}
                >
                  {column.headerName}
                </TableCell>
              ))}
              {renderActions && <TableCell>Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell 
                  colSpan={renderActions ? columns.length + 1 : columns.length} 
                  align="center"
                  sx={{ py: 4 }}
                >
                  <CircularProgress size={24} sx={{ mr: 1 }} />
                  <Typography variant="body2" component="span">
                    Loading...
                  </Typography>
                </TableCell>
              </TableRow>
            ) : data.length > 0 ? (
              data.map((row, index) => {
                const rowKey = 'id' in row && row.id ? String(row.id) : index;
                return (
                  <TableRow 
                    key={rowKey}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                      }
                    }}
                  >
                    {columns.map((column) => (
                      <TableCell key={`${rowKey}-${String(column.field)}`}>
                        {column.renderCell 
                          ? column.renderCell(row) 
                          : row[column.field]}
                      </TableCell>
                    ))}
                    {renderActions && (
                      <TableCell>
                        {renderActions(row)}
                      </TableCell>
                    )}
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell 
                  colSpan={renderActions ? columns.length + 1 : columns.length} 
                  align="center"
                  sx={{ py: 3 }}
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {totalPages > 1 && onPageChange && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination 
            count={totalPages} 
            page={page} 
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
};

export default DataTable; 