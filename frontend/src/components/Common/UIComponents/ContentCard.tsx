import React from 'react';
import { Card, CardContent } from '@mui/material';

interface ContentCardProps {
  children: React.ReactNode;
  elevation?: number;
  padding?: number | string;
  fullHeight?: boolean;
  gradient?: boolean;
}

const ContentCard: React.FC<ContentCardProps> = ({
  children,
  elevation = 1,
  padding = 3,
  fullHeight = false,
  gradient = false,
}) => {
  return (
    <Card
      elevation={elevation}
      sx={{
        borderRadius: 4,
        background: gradient 
          ? 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)'
          : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        boxShadow: gradient 
          ? '0px 8px 32px rgba(0, 0, 0, 0.08), 0px 1px 2px rgba(0, 0, 0, 0.05)'
          : '0px 4px 20px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.3s ease-in-out',
        height: fullHeight ? '100%' : 'auto',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0px 12px 40px rgba(0, 0, 0, 0.12)',
        },
        '&::before': gradient ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          zIndex: 1,
        } : {},
      }}
    >
      <CardContent
        sx={{
          p: padding,
          '&:last-child': {
            pb: padding,
          },
          position: 'relative',
          zIndex: 2,
        }}
      >
        {children}
      </CardContent>
    </Card>
  );
};

export default ContentCard; 