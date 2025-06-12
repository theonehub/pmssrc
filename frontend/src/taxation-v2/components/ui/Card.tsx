import React from 'react';
import {
  Card as MuiCard,
  CardProps as MuiCardProps,
  CardContent,
  CardHeader,
  CardActions,
  Box,
  Typography,
  IconButton,
  Collapse,
  Skeleton
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { ExpandMore, ExpandLess } from '@mui/icons-material';

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

interface StyledCardProps {
  customVariant?: 'gradient' | 'success' | 'warning' | 'error' | 'info' | undefined;
  elevation?: number;
}

const StyledCard = styled(MuiCard)<StyledCardProps>(({ theme, customVariant, elevation }) => ({
  borderRadius: 12,
  boxShadow: elevation === 0 ? 'none' : theme.shadows[elevation || 2],
  transition: 'all 0.3s ease-in-out',
  
  // Mobile-friendly spacing
  '@media (max-width: 768px)': {
    borderRadius: 8,
    margin: theme.spacing(1),
  },
  
  // Custom variant styles
  ...(customVariant === 'gradient' && {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: theme.palette.common.white,
    
    '& .MuiCardHeader-title': {
      color: theme.palette.common.white,
    },
    
    '& .MuiCardHeader-subheader': {
      color: theme.palette.grey[100],
    },
  }),
  
  ...(customVariant === 'success' && {
    borderLeft: `4px solid ${theme.palette.success.main}`,
    backgroundColor: theme.palette.success.light + '10',
  }),
  
  ...(customVariant === 'warning' && {
    borderLeft: `4px solid ${theme.palette.warning.main}`,
    backgroundColor: theme.palette.warning.light + '10',
  }),
  
  ...(customVariant === 'error' && {
    borderLeft: `4px solid ${theme.palette.error.main}`,
    backgroundColor: theme.palette.error.light + '10',
  }),
  
  ...(customVariant === 'info' && {
    borderLeft: `4px solid ${theme.palette.info.main}`,
    backgroundColor: theme.palette.info.light + '10',
  }),
  
  // Hover effects
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[elevation ? elevation + 2 : 4],
  },
  
  // Clickable card
  '&.clickable': {
    cursor: 'pointer',
    
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows[8],
    },
  },
}));

const LoadingContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  
  '@media (max-width: 768px)': {
    padding: theme.spacing(2),
  },
}));

// =============================================================================
// COMPONENT INTERFACES
// =============================================================================

export interface CardProps extends Omit<MuiCardProps, 'variant'> {
  variant?: 'elevation' | 'outlined' | 'gradient' | 'success' | 'warning' | 'error' | 'info';
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  loading?: boolean;
  onClick?: () => void;
  headerContent?: React.ReactNode;
  actionsContent?: React.ReactNode;
  mobile?: boolean;
}

// =============================================================================
// CARD COMPONENT
// =============================================================================

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'elevation',
  title,
  subtitle,
  action,
  collapsible = false,
  defaultExpanded = true,
  loading = false,
  onClick,
  headerContent,
  actionsContent,
  mobile = false,
  elevation = 2,
  ...props
}) => {
  const [expanded, setExpanded] = React.useState(defaultExpanded);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleCardClick = () => {
    if (onClick && !collapsible) {
      onClick();
    }
  };

  // Determine MUI variant and custom variant
  const muiVariant = variant === 'outlined' ? 'outlined' : 'elevation';
  const customVariant = ['gradient', 'success', 'warning', 'error', 'info'].includes(variant) 
    ? variant as 'gradient' | 'success' | 'warning' | 'error' | 'info'
    : undefined;

  // Loading state
  if (loading) {
    return (
      <StyledCard 
        variant={muiVariant} 
        customVariant={customVariant}
        elevation={elevation} 
        {...props}
      >
        <LoadingContainer>
          <Skeleton variant="text" height={24} width="60%" sx={{ mb: 1 }} />
          <Skeleton variant="text" height={16} width="40%" sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" height={120} />
        </LoadingContainer>
      </StyledCard>
    );
  }

  return (
    <StyledCard
      variant={muiVariant}
      customVariant={customVariant}
      elevation={elevation}
      onClick={handleCardClick}
      className={onClick && !collapsible ? 'clickable' : ''}
      {...props}
    >
      {/* Header */}
      {(title || subtitle || action || headerContent || collapsible) && (
        <CardHeader
          title={title}
          subheader={subtitle}
          action={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {action}
              {headerContent}
              {collapsible && (
                <IconButton
                  onClick={handleExpandClick}
                  aria-expanded={expanded}
                  aria-label="expand"
                  size={mobile ? 'large' : 'medium'}
                >
                  {expanded ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              )}
            </Box>
          }
          sx={{
            pb: title || subtitle ? 1 : 0,
            
            '& .MuiCardHeader-title': {
              fontSize: mobile ? '1.25rem' : '1.125rem',
              fontWeight: 600,
            },
            
            '& .MuiCardHeader-subheader': {
              fontSize: mobile ? '0.875rem' : '0.8rem',
            },
          }}
        />
      )}

      {/* Content */}
      <Collapse in={!collapsible || expanded} timeout="auto" unmountOnExit>
        <CardContent
          sx={{
            pt: (title || subtitle) ? 0 : undefined,
            pb: actionsContent ? 1 : undefined,
            
            '&:last-child': {
              pb: actionsContent ? 1 : 2,
            },
            
            '@media (max-width: 768px)': {
              padding: mobile ? '12px 16px' : '16px',
            },
          }}
        >
          {children}
        </CardContent>
      </Collapse>

      {/* Actions */}
      {actionsContent && (
        <CardActions
          sx={{
            pt: 0,
            px: 2,
            pb: 2,
            
            '@media (max-width: 768px)': {
              px: mobile ? 2 : 1.5,
              flexDirection: 'column',
              gap: 1,
              
              '& > *': {
                width: '100%',
              },
            },
          }}
        >
          {actionsContent}
        </CardActions>
      )}
    </StyledCard>
  );
};

// =============================================================================
// SPECIALIZED CARD COMPONENTS
// =============================================================================

export const InfoCard: React.FC<Omit<CardProps, 'variant'>> = (props) => (
  <Card variant="info" {...props} />
);

export const SuccessCard: React.FC<Omit<CardProps, 'variant'>> = (props) => (
  <Card variant="success" {...props} />
);

export const WarningCard: React.FC<Omit<CardProps, 'variant'>> = (props) => (
  <Card variant="warning" {...props} />
);

export const ErrorCard: React.FC<Omit<CardProps, 'variant'>> = (props) => (
  <Card variant="error" {...props} />
);

export const GradientCard: React.FC<Omit<CardProps, 'variant'>> = (props) => (
  <Card variant="gradient" {...props} />
);

// =============================================================================
// CALCULATION RESULT CARD
// =============================================================================

interface CalculationCardProps extends Omit<CardProps, 'children'> {
  label: string;
  amount: number;
  previousAmount?: number;
  currency?: boolean;
  percentage?: boolean;
  trend?: 'up' | 'down' | 'neutral';
  loading?: boolean;
}

export const CalculationCard: React.FC<CalculationCardProps> = ({
  label,
  amount,
  previousAmount,
  currency = true,
  percentage = false,
  trend,
  loading = false,
  ...cardProps
}) => {
  const formatAmount = (value: number) => {
    if (currency) {
      return `₹${value.toLocaleString('en-IN')}`;
    } else if (percentage) {
      return `${value.toFixed(2)}%`;
    }
    return value.toLocaleString('en-IN');
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'success.main';
      case 'down': return 'error.main';
      default: return 'text.primary';
    }
  };

  const renderTrendIcon = () => {
    if (!trend || trend === 'neutral') return null;
    // We can add trend icons here if needed
    return null;
  };

  return (
    <Card loading={loading} {...cardProps}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {label}
          </Typography>
          <Typography variant="h5" fontWeight="bold" color={getTrendColor()}>
            {formatAmount(amount)}
            {renderTrendIcon()}
          </Typography>
          {previousAmount !== undefined && (
            <Typography variant="caption" color="text.secondary">
              Previous: {formatAmount(previousAmount)}
            </Typography>
          )}
        </Box>
      </Box>
    </Card>
  );
};

export default Card; 