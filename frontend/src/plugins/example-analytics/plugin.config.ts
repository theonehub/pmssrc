import { PluginConfig } from '../../shared/types/plugin';

const analyticsPlugin: PluginConfig = {
  id: 'analytics-plugin',
  name: 'Advanced Analytics',
  version: '1.0.0',
  description: 'Advanced analytics and reporting features',
  enabled: true, // This determines if the plugin should be shown
  menuCategories: [
    {
      id: 'analytics',
      title: 'Advanced Analytics',
      icon: 'AnalyticsIcon',
      priority: 10, // Higher priority means it appears earlier in the menu
      items: [
        {
          title: 'Performance Dashboard',
          icon: 'TrendingUpIcon',
          path: '/performance-dashboard',
          roles: ['manager', 'admin', 'superadmin'],
        },
        {
          title: 'Revenue Analytics',
          icon: 'PieChartIcon',
          path: '/revenue-analytics',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'Custom Reports',
          icon: 'BarChartIcon',
          path: '/custom-reports',
          roles: ['manager', 'admin', 'superadmin'],
        },
      ],
    },
  ],
  dependencies: [],
  permissions: ['analytics.read', 'reports.create'],
};

export default analyticsPlugin; 