import React from 'react';
import { TextField, InputAdornment, SxProps, Theme, TextFieldProps } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

// Define interfaces
interface SearchInputProps {
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  sx?: SxProps<Theme>;
  textFieldProps?: Omit<TextFieldProps, 'value' | 'onChange' | 'placeholder' | 'sx'>;
}

/**
 * Reusable search input component with Material-UI styling
 */
const SearchInput: React.FC<SearchInputProps> = ({
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

export default SearchInput; 