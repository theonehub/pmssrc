import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogProps,
  IconButton,
  Box,
  Typography,
  Slide,
  Fade,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { Close } from '@mui/icons-material';
import { TransitionProps } from '@mui/material/transitions';

// =============================================================================
// TRANSITIONS
// =============================================================================

const SlideTransition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>;
  },
  ref: React.Ref<unknown>,
) {
  const { children, appear, enter, exit, in: inProp, ...cleanProps } = props;
  const slideProps: any = { ...cleanProps };
  
  // Only add boolean props if they're explicitly defined
  if (appear !== undefined) slideProps.appear = appear;
  if (enter !== undefined) slideProps.enter = enter;
  if (exit !== undefined) slideProps.exit = exit;
  if (inProp !== undefined) slideProps.in = inProp;
  
  return <Slide direction="up" ref={ref} {...slideProps}>{children}</Slide>;
});

const FadeTransition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>;
  },
  ref: React.Ref<unknown>,
) {
  const { children, appear, enter, exit, in: inProp, ...cleanProps } = props;
  const fadeProps: any = { ...cleanProps };
  
  // Only add boolean props if they're explicitly defined
  if (appear !== undefined) fadeProps.appear = appear;
  if (enter !== undefined) fadeProps.enter = enter;
  if (exit !== undefined) fadeProps.exit = exit;
  if (inProp !== undefined) fadeProps.in = inProp;
  
  return <Fade ref={ref} {...fadeProps}>{children}</Fade>;
});

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const StyledDialog = styled(Dialog)<{ size?: string }>(({ theme, size }) => ({
  '& .MuiDialog-paper': {
    borderRadius: 12,
    maxHeight: '90vh',
    
    // Size variants
    ...(size === 'small' && {
      maxWidth: 400,
      width: '100%',
    }),
    
    ...(size === 'medium' && {
      maxWidth: 600,
      width: '100%',
    }),
    
    ...(size === 'large' && {
      maxWidth: 900,
      width: '100%',
    }),
    
    ...(size === 'fullscreen' && {
      maxWidth: '100vw',
      maxHeight: '100vh',
      width: '100vw',
      height: '100vh',
      margin: 0,
      borderRadius: 0,
    }),
    
    // Mobile responsiveness
    '@media (max-width: 768px)': {
      margin: theme.spacing(2),
      width: `calc(100vw - ${theme.spacing(4)})`,
      maxHeight: `calc(100vh - ${theme.spacing(4)})`,
      
      ...(size === 'fullscreen' && {
        margin: 0,
        width: '100vw',
        height: '100vh',
        maxWidth: '100vw',
        maxHeight: '100vh',
        borderRadius: 0,
      }),
    },
  },
}));

const StyledDialogTitle = styled(DialogTitle)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${theme.palette.divider}`,
  
  '& .MuiTypography-root': {
    fontSize: '1.25rem',
    fontWeight: 600,
  },
  
  '@media (max-width: 768px)': {
    padding: theme.spacing(2),
    
    '& .MuiTypography-root': {
      fontSize: '1.125rem',
    },
  },
}));

const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(3),
  
  '&.MuiDialogContent-dividers': {
    borderTop: `1px solid ${theme.palette.divider}`,
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  
  '@media (max-width: 768px)': {
    padding: theme.spacing(2),
  },
}));

const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderTop: `1px solid ${theme.palette.divider}`,
  gap: theme.spacing(1),
  
  '@media (max-width: 768px)': {
    padding: theme.spacing(2),
    flexDirection: 'column-reverse',
    
    '& > *': {
      width: '100%',
      margin: 0,
    },
  },
}));

// =============================================================================
// COMPONENT INTERFACES
// =============================================================================

export interface ModalProps extends Omit<DialogProps, 'title'> {
  title?: string;
  subtitle?: string;
  size?: 'small' | 'medium' | 'large' | 'fullscreen' | 'auto';
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscapeKey?: boolean;
  actionsContent?: React.ReactNode;
  headerContent?: React.ReactNode;
  transition?: 'slide' | 'fade';
  mobile?: boolean;
  loading?: boolean;
}

// =============================================================================
// MODAL COMPONENT
// =============================================================================

export const Modal: React.FC<ModalProps> = ({
  children,
  title,
  subtitle,
  size = 'medium',
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscapeKey = true,
  actionsContent,
  headerContent,
  transition = 'slide',
  mobile = false,
  loading = false,
  open,
  onClose,
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const actuallyMobile = mobile || isMobile;

  const handleClose = (event: object, reason: 'backdropClick' | 'escapeKeyDown') => {
    if (reason === 'backdropClick' && !closeOnBackdropClick) return;
    if (reason === 'escapeKeyDown' && !closeOnEscapeKey) return;
    
    if (onClose) {
      onClose(event, reason);
    }
  };

  const handleCloseButtonClick = (event: React.MouseEvent) => {
    if (onClose) {
      onClose(event, 'backdropClick'); // Use backdropClick as fallback for close button
    }
  };

  const getTransitionComponent = () => {
    switch (transition) {
      case 'fade':
        return FadeTransition;
      case 'slide':
      default:
        return SlideTransition;
    }
  };

  const renderHeader = () => {
    if (!title && !headerContent && !showCloseButton) return null;

    return (
      <StyledDialogTitle>
        <Box>
          {title && (
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {headerContent}
          {showCloseButton && (
            <IconButton
              aria-label="close"
              onClick={handleCloseButtonClick}
              size={actuallyMobile ? 'large' : 'medium'}
              sx={{
                color: (theme) => theme.palette.grey[500],
              }}
            >
              <Close />
            </IconButton>
          )}
        </Box>
      </StyledDialogTitle>
    );
  };

  const renderContent = () => {
    if (loading) {
      return (
        <StyledDialogContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 200,
            }}
          >
            <Typography>Loading...</Typography>
          </Box>
        </StyledDialogContent>
      );
    }

    return (
      <StyledDialogContent dividers={!!actionsContent}>
        {children}
      </StyledDialogContent>
    );
  };

  const renderActions = () => {
    if (!actionsContent) return null;

    return (
      <StyledDialogActions>
        {actionsContent}
      </StyledDialogActions>
    );
  };

  return (
    <StyledDialog
      open={open}
      onClose={handleClose}
      size={actuallyMobile ? 'fullscreen' : size}
      fullScreen={actuallyMobile && size === 'fullscreen'}
      TransitionComponent={getTransitionComponent()}
      {...props}
    >
      {renderHeader()}
      {renderContent()}
      {renderActions()}
    </StyledDialog>
  );
};

// =============================================================================
// SPECIALIZED MODAL COMPONENTS
// =============================================================================

export const ConfirmModal: React.FC<Omit<ModalProps, 'actionsContent'> & {
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
}> = ({
  onConfirm,
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmColor = 'primary',
  ...modalProps
}) => {
  return (
    <Modal
      {...modalProps}
      actionsContent={
        <>
          <button onClick={onCancel}>{cancelText}</button>
          <button onClick={onConfirm}>{confirmText}</button>
        </>
      }
    />
  );
};

export const AlertModal: React.FC<Omit<ModalProps, 'actionsContent'> & {
  onClose: () => void;
  closeText?: string;
}> = ({
  onClose,
  closeText = 'OK',
  ...modalProps
}) => {
  return (
    <Modal
      {...modalProps}
      onClose={onClose}
      actionsContent={
        <button onClick={onClose}>{closeText}</button>
      }
    />
  );
};

export const FormModal: React.FC<ModalProps & {
  onSubmit?: () => void;
  onCancel?: () => void;
  submitText?: string;
  cancelText?: string;
  submitDisabled?: boolean;
}> = ({
  onSubmit,
  onCancel,
  submitText = 'Submit',
  cancelText = 'Cancel',
  submitDisabled = false,
  ...modalProps
}) => {
  return (
    <Modal
      {...modalProps}
      actionsContent={
        <>
          {onCancel && <button onClick={onCancel}>{cancelText}</button>}
          {onSubmit && (
            <button 
              onClick={onSubmit} 
              disabled={submitDisabled}
            >
              {submitText}
            </button>
          )}
        </>
      }
    />
  );
};

export default Modal; 