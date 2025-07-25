import { Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

export const theme = {
  // Colors matching your web app
  colors: {
    primary: '#1976d2', // Match your web app primary color
    primaryDark: '#1565c0',
    primaryLight: '#42a5f5',
    secondary: '#dc004e',
    secondaryDark: '#c51162',
    secondaryLight: '#ff5983',
    background: '#fafafa',
    surface: '#ffffff',
    error: '#b00020',
    warning: '#ff9800',
    success: '#4caf50',
    info: '#2196f3',
    text: {
      primary: '#000000',
      secondary: '#666666',
      disabled: '#999999',
      inverse: '#ffffff',
    },
    onSurface: '#000000',
    disabled: '#cccccc',
    placeholder: '#9e9e9e',
    backdrop: 'rgba(0, 0, 0, 0.5)',
    notification: '#ff9800',
    border: '#e0e0e0',
    divider: '#f0f0f0',
  },
  
  // Typography that works well on mobile
  typography: {
    h1: { 
      fontSize: 24, 
      fontWeight: 'bold' as const,
      lineHeight: 32,
    },
    h2: { 
      fontSize: 20, 
      fontWeight: 'bold' as const,
      lineHeight: 28,
    },
    h3: { 
      fontSize: 18, 
      fontWeight: '600' as const,
      lineHeight: 24,
    },
    h4: { 
      fontSize: 16, 
      fontWeight: '600' as const,
      lineHeight: 22,
    },
    body1: { 
      fontSize: 16,
      lineHeight: 24,
    },
    body2: { 
      fontSize: 14,
      lineHeight: 20,
    },
    caption: { 
      fontSize: 12,
      lineHeight: 16,
    },
    button: {
      fontSize: 14,
      fontWeight: '600' as const,
      textTransform: 'uppercase' as const,
    },
  },
  
  // Spacing that's mobile-friendly
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },

  // Border radius
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    round: 50,
  },

  // Shadows
  shadows: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.15,
      shadowRadius: 4,
      elevation: 4,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.2,
      shadowRadius: 8,
      elevation: 8,
    },
  },

  // Layout
  layout: {
    screenWidth: width,
    screenHeight: height,
    headerHeight: 56,
    tabBarHeight: 80,
    bottomSafeArea: 34,
  },

  // Animation
  animation: {
    duration: {
      fast: 200,
      normal: 300,
      slow: 500,
    },
    easing: {
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out',
    },
  },
};

// Responsive helpers
export const isSmallDevice = width < 375;
export const isMediumDevice = width >= 375 && width < 414;
export const isLargeDevice = width >= 414;

// Responsive spacing
export const responsiveSpacing = {
  xs: isSmallDevice ? 2 : 4,
  sm: isSmallDevice ? 6 : 8,
  md: isSmallDevice ? 12 : 16,
  lg: isSmallDevice ? 18 : 24,
  xl: isSmallDevice ? 24 : 32,
  xxl: isSmallDevice ? 36 : 48,
};

// Responsive typography
export const responsiveTypography = {
  h1: { 
    fontSize: isSmallDevice ? 20 : 24, 
    fontWeight: 'bold' as const,
    lineHeight: isSmallDevice ? 28 : 32,
  },
  h2: { 
    fontSize: isSmallDevice ? 18 : 20, 
    fontWeight: 'bold' as const,
    lineHeight: isSmallDevice ? 24 : 28,
  },
  h3: { 
    fontSize: isSmallDevice ? 16 : 18, 
    fontWeight: '600' as const,
    lineHeight: isSmallDevice ? 22 : 24,
  },
  body1: { 
    fontSize: isSmallDevice ? 14 : 16,
    lineHeight: isSmallDevice ? 20 : 24,
  },
  body2: { 
    fontSize: isSmallDevice ? 12 : 14,
    lineHeight: isSmallDevice ? 18 : 20,
  },
};

export type Theme = typeof theme;
export type Colors = typeof theme.colors;
export type Typography = typeof theme.typography;
export type Spacing = typeof theme.spacing; 