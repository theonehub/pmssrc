import React from 'react';
import PropTypes from 'prop-types';
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

/**
 * Reusable data table component with Material-UI styling
 * 
 * @param {Object} props - Component props
 * @param {Array} props.columns - Column configuration array with 'field', 'headerName', and optional 'renderCell' and 'width' properties
 * @param {Array} props.data - Data array to display in the table
 * @param {boolean} props.loading - Whether the data is loading
 * @param {string} props.emptyMessage - Message to display when there's no data
 * @param {function} props.renderActions - Optional function to render action buttons for each row
 * @param {number} props.page - Current page for pagination
 * @param {number} props.totalPages - Total number of pages
 * @param {function} props.onPageChange - Function to handle page changes
 * @param {string} props.title - Optional table title
 */
const DataTable = ({
  columns,
  data,
  loading,
  emptyMessage = 'No data found',
  renderActions,
  page = 1,
  totalPages = 1,
  onPageChange,
  title
}) => {
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
                  key={column.field} 
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
              data.map((row, index) => (
                <TableRow 
                  key={row.id || index}
                  sx={{ 
                    '&:hover': { 
                      backgroundColor: 'action.hover',
                    }
                  }}
                >
                  {columns.map((column) => (
                    <TableCell key={`${row.id || index}-${column.field}`}>
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
              ))
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
      
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination 
            count={totalPages} 
            page={page} 
            onChange={(event, value) => onPageChange(value)}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
};

DataTable.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      field: PropTypes.string.isRequired,
      headerName: PropTypes.string.isRequired,
      renderCell: PropTypes.func,
      width: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    })
  ).isRequired,
  data: PropTypes.array.isRequired,
  loading: PropTypes.bool,
  emptyMessage: PropTypes.string,
  renderActions: PropTypes.func,
  page: PropTypes.number,
  totalPages: PropTypes.number,
  onPageChange: PropTypes.func,
  title: PropTypes.string
};

export default DataTable; 