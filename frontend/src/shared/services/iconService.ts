import React from 'react';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
  Inventory as InventoryIcon,
  Category as CategoryIcon,
  LocalShipping as ShippingIcon,
  QrCode as QrCodeIcon,
  Home as HomeIcon,
  People as PeopleIcon,
  CalendarToday as CalendarIcon,
  Receipt as ReceiptIcon,
  Settings as SettingsIcon,
  Business as BusinessIcon,
  CurrencyRupee as CurrencyRupeeIcon,
  AccountBalance as AccountBalanceIcon,
  Assessment as AssessmentIcon,
  Extension as ExtensionIcon,
  Security as SecurityIcon,
  Info as InfoIcon,
  AccountBalanceWallet as AccountBalanceWalletIcon,
  List as ListIcon,
  Add as AddIcon,
  Functions as FunctionsIcon,
  PersonPin as PersonPinIcon,
} from '@mui/icons-material';

export const iconMap: { [key: string]: React.ReactElement } = {
  // Analytics plugin icons
  AnalyticsIcon: React.createElement(AnalyticsIcon),
  TrendingUpIcon: React.createElement(TrendingUpIcon),
  PieChartIcon: React.createElement(PieChartIcon),
  BarChartIcon: React.createElement(BarChartIcon),
  
  // Inventory plugin icons
  InventoryIcon: React.createElement(InventoryIcon),
  CategoryIcon: React.createElement(CategoryIcon),
  ShippingIcon: React.createElement(ShippingIcon),
  QrCodeIcon: React.createElement(QrCodeIcon),
  
  // Salary Components plugin icons
  AccountBalanceWalletIcon: React.createElement(AccountBalanceWalletIcon),
  ListIcon: React.createElement(ListIcon),
  AddIcon: React.createElement(AddIcon),
  FunctionsIcon: React.createElement(FunctionsIcon),
  PersonPinIcon: React.createElement(PersonPinIcon),
  
  // Core app icons
  HomeIcon: React.createElement(HomeIcon),
  PeopleIcon: React.createElement(PeopleIcon),
  CalendarIcon: React.createElement(CalendarIcon),
  ReceiptIcon: React.createElement(ReceiptIcon),
  SettingsIcon: React.createElement(SettingsIcon),
  BusinessIcon: React.createElement(BusinessIcon),
  CurrencyRupeeIcon: React.createElement(CurrencyRupeeIcon),
  AccountBalanceIcon: React.createElement(AccountBalanceIcon),
  AssessmentIcon: React.createElement(AssessmentIcon),
  ExtensionIcon: React.createElement(ExtensionIcon),
  SecurityIcon: React.createElement(SecurityIcon),
  InfoIcon: React.createElement(InfoIcon),
};

export const getIcon = (iconName: string): React.ReactElement => {
  return iconMap[iconName] || React.createElement(ExtensionIcon);
}; 