import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const StyledButton = styled(MuiButton)<{ isGradient?: boolean }>(({ size, isGradient }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  minHeight: size === 'small' ? 36 : size === 'large' ? 48 : 40,
  padding: size === 'small' ? '8px 16px' : size === 'large' ? '12px 24px' : '10px 20px',
  
  // Mobile-friendly touch targets
  '@media (max-width: 768px)': {
    minHeight: size === 'small' ? 40 : size === 'large' ? 52 : 44,
    fontSize: size === 'small' ? '0.875rem' : '1rem',
  },
  
  // Loading state
  '&.loading': {
    pointerEvents: 'none',
  },
  
  // Custom gradient variant
  ...(isGradient && {
    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
    border: 0,
    color: 'white',
    '&:hover': {
      background: 'linear-gradient(45deg, #1976D2 30%, #0288D1 90%)',
    },
  }),
}));

// =============================================================================
// COMPONENT INTERFACE
// =============================================================================

export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?: 'text' | 'outlined' | 'contained' | 'gradient';
  loading?: boolean;
  loadingText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'start' | 'end';
  fullWidth?: boolean;
  mobile?: boolean;
}

// =============================================================================
// BUTTON COMPONENT
// =============================================================================

export const Button: React.FC<ButtonProps> = ({
  children,
  loading = false,
  loadingText,
  icon,
  iconPosition = 'start',
  disabled,
  variant = 'contained',
  size = 'medium',
  mobile = false,
  onClick,
  ...props
}) => {
  const isDisabled = disabled || loading;
  const displayText = loading && loadingText ? loadingText : children;
  
  const startIcon = loading ? (
    <CircularProgress size={16} color="inherit" />
  ) : (
    iconPosition === 'start' && icon ? icon : undefined
  );
  
  const endIcon = !loading && iconPosition === 'end' && icon ? icon : undefined;

  return (
    <StyledButton
      {...props}
      variant={variant === 'gradient' ? 'contained' : variant}
      size={mobile ? 'large' : size}
      disabled={isDisabled}
      onClick={onClick}
      startIcon={startIcon}
      endIcon={endIcon}
      className={loading ? 'loading' : ''}
      isGradient={variant === 'gradient'}
    >
      {displayText}
    </StyledButton>
  );
};

// =============================================================================
// BUTTON VARIANTS
// =============================================================================

export const PrimaryButton: React.FC<ButtonProps> = (props) => (
  <Button variant="contained" color="primary" {...props} />
);

export const SecondaryButton: React.FC<ButtonProps> = (props) => (
  <Button variant="outlined" color="primary" {...props} />
);

export const DangerButton: React.FC<ButtonProps> = (props) => (
  <Button variant="contained" color="error" {...props} />
);

export const GradientButton: React.FC<ButtonProps> = (props) => (
  <Button variant="gradient" {...props} />
);

export default Button; 