import React from 'react';
import PropTypes from 'prop-types';
import { TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

/**
 * Reusable search input component with Material-UI styling
 * 
 * @param {Object} props - Component props
 * @param {string} props.value - Current search value
 * @param {function} props.onChange - Function to handle value changes
 * @param {string} props.placeholder - Placeholder text
 * @param {Object} props.sx - Additional styles for the input
 * @param {Object} props.textFieldProps - Additional props for the TextField component
 */
const SearchInput = ({
  value,
  onChange,
  placeholder = 'Search...',
  sx = {},
  textFieldProps = {}
}) => {
  return (
    <TextField
      fullWidth
      variant="outlined"
      size="small"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon />
          </InputAdornment>
        ),
      }}
      sx={{ 
        mb: 3,
        ...sx 
      }}
      {...textFieldProps}
    />
  );
};

SearchInput.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  sx: PropTypes.object,
  textFieldProps: PropTypes.object
};

export default SearchInput; 