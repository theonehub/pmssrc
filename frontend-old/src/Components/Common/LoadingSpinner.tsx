import React from 'react';
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Backdrop,
  SxProps,
  Theme,
} from '@mui/material';

// Define the variant types
type LoadingVariant = 'circular' | 'linear' | 'overlay' | 'inline';
type LoadingSize = 'small' | 'medium' | 'large';

// Define the props interface
interface LoadingSpinnerProps {
  variant?: LoadingVariant;
  size?: LoadingSize;
  message?: string;
  fullScreen?: boolean;
  sx?: SxProps<Theme>;
  [key: string]: any; // For additional props
}

/**
 * LoadingSpinner - A versatile loading component with multiple variants
 * 
 * @param props - Component props
 * @param props.variant - Loading variant: 'circular', 'linear', 'overlay', 'inline'
 * @param props.size - Size for circular progress: 'small', 'medium', 'large'
 * @param props.message - Optional loading message
 * @param props.fullScreen - Whether to show as full screen overlay
 * @param props.sx - Additional MUI sx props
 * @returns Loading spinner component
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  variant = 'circular',
  size = 'medium',
  message = '',
  fullScreen = false,
  sx = {},
  ...props
}) => {
  const getSizeValue = (): number => {
    switch (size) {
      case 'small':
        return 24;
      case 'large':
        return 60;
      case 'medium':
      default:
        return 40;
    }
  };

  const renderCircularProgress = (): React.ReactElement => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        ...sx,
      }}
      {...props}
    >
      <CircularProgress size={getSizeValue()} />
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );

  const renderLinearProgress = (): React.ReactElement => (
    <Box sx={{ width: '100%', ...sx }} {...props}>
      {message && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {message}
        </Typography>
      )}
      <LinearProgress />
    </Box>
  );

  const renderInlineProgress = (): React.ReactElement => (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 1,
        ...sx,
      }}
      {...props}
    >
      <CircularProgress size={20} />
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );

  const renderOverlayProgress = (): React.ReactElement => (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        zIndex: 1000,
        gap: 2,
        ...sx,
      }}
      {...props}
    >
      <CircularProgress size={getSizeValue()} />
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );

  const renderContent = (): React.ReactElement => {
    switch (variant) {
      case 'linear':
        return renderLinearProgress();
      case 'inline':
        return renderInlineProgress();
      case 'overlay':
        return renderOverlayProgress();
      case 'circular':
      default:
        return renderCircularProgress();
    }
  };

  if (fullScreen) {
    return (
      <Backdrop
        sx={{
          color: '#fff',
          zIndex: (theme: Theme) => theme.zIndex.drawer + 1,
          flexDirection: 'column',
          gap: 2,
        }}
        open={true}
      >
        <CircularProgress color="inherit" size={getSizeValue()} />
        {message && (
          <Typography variant="h6" color="inherit">
            {message}
          </Typography>
        )}
      </Backdrop>
    );
  }

  return renderContent();
};

export default LoadingSpinner; 