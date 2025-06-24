import { PluginConfig } from '../shared/types/plugin';

// This utility demonstrates how to initialize plugins for testing
// In a real application, plugins would be loaded from a server or plugin marketplace

export const initializeDefaultPlugins = () => {
  // Check if plugins are already initialized
  const existingPlugins = localStorage.getItem('pms_plugins');
  if (existingPlugins) {
    console.log('Plugins already initialized');
    // Force reinitialize if salary-components-plugin is missing
    const parsedPlugins = JSON.parse(existingPlugins);
    const hasSalaryComponents = parsedPlugins.some((p: any) => p.id === 'salary-components-plugin');
    if (hasSalaryComponents) {
      return;
    }
    console.log('Salary Components plugin missing, reinitializing...');
  }

  // Default plugins for demonstration
  const defaultPlugins: PluginConfig[] = [
    {
      id: 'analytics-plugin',
      name: 'Advanced Analytics',
      version: '1.0.0',
      description: 'Advanced analytics and reporting features',
      enabled: true,
      menuCategories: [
        {
          id: 'analytics',
          title: 'Advanced Analytics',
                     icon: 'AnalyticsIcon',
          priority: 10,
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
          ],
        },
      ],
      permissions: ['analytics.read'],
    },
    {
      id: 'salary-components-plugin',
      name: 'Salary Components',
      version: '1.0.0',
      description: 'Complete salary component management system with formula-based calculations',
      enabled: true,
      menuCategories: [
        {
          id: 'salary-components',
          title: 'Salary Components',
          icon: 'AccountBalanceWalletIcon',
          priority: 8,
          items: [
            {
              title: 'Components List',
              icon: 'ListIcon',
              path: '/salary-components',
              roles: ['user', 'manager', 'admin', 'superadmin', 'hr'],
            },
            {
              title: 'Create Component',
              icon: 'AddIcon',
              path: '/salary-components/create',
              roles: ['manager', 'admin', 'superadmin'],
            },
            {
              title: 'Assign Components',
              icon: 'AssignmentIcon',
              path: '/salary-components/assign',
              roles: ['superadmin'],
            },
            {
              title: 'Formula Builder',
              icon: 'FunctionsIcon',
              path: '/salary-components/formula-builder',
              roles: ['manager', 'admin', 'superadmin'],
            },
            {
              title: 'Employee Mapping',
              icon: 'PersonPinIcon',
              path: '/salary-components/employee-mapping',
              roles: ['user', 'manager', 'admin', 'superadmin', 'hr'],
            },
          ],
        },
      ],
      permissions: ['salary.read', 'salary.write', 'salary.manage'],
    },
    {
      id: 'inventory-plugin',
      name: 'Inventory Management',
      version: '2.1.0',
      description: 'Complete inventory management system',
      enabled: false, // Disabled by default
      menuCategories: [
        {
          id: 'inventory',
          title: 'Inventory',
          icon: 'InventoryIcon',
          priority: 5,
          items: [
            {
              title: 'Product Catalog',
              icon: 'CategoryIcon',
              path: '/product-catalog',
              roles: ['manager', 'admin', 'superadmin'],
            },
            {
              title: 'Stock Management',
              icon: 'InventoryIcon',
              path: '/stock-management',
              roles: ['admin', 'superadmin'],
            },
          ],
        },
      ],
      permissions: ['inventory.read', 'inventory.write'],
    },
  ];

  // Save to localStorage
  localStorage.setItem('pms_plugins', JSON.stringify(defaultPlugins));
  console.log('Default plugins initialized');
};

export const enablePlugin = (pluginId: string) => {
  const plugins = getStoredPlugins();
  const updatedPlugins = plugins.map(plugin =>
    plugin.id === pluginId ? { ...plugin, enabled: true } : plugin
  );
  localStorage.setItem('pms_plugins', JSON.stringify(updatedPlugins));
  console.log(`Plugin ${pluginId} enabled`);
};

export const disablePlugin = (pluginId: string) => {
  const plugins = getStoredPlugins();
  const updatedPlugins = plugins.map(plugin =>
    plugin.id === pluginId ? { ...plugin, enabled: false } : plugin
  );
  localStorage.setItem('pms_plugins', JSON.stringify(updatedPlugins));
  console.log(`Plugin ${pluginId} disabled`);
};

export const getStoredPlugins = (): PluginConfig[] => {
  const plugins = localStorage.getItem('pms_plugins');
  return plugins ? JSON.parse(plugins) : [];
};

export const clearPlugins = () => {
  localStorage.removeItem('pms_plugins');
  console.log('All plugins cleared');
};

export const forceReinitializePlugins = () => {
  clearPlugins();
  initializeDefaultPlugins();
  console.log('Plugins force reinitialized');
};

export const debugPlugins = () => {
  console.log('=== Plugin Debug Information ===');
  
  // Check localStorage
  const storedPlugins = localStorage.getItem('pms_plugins');
  console.log('1. Stored plugins in localStorage:', storedPlugins ? JSON.parse(storedPlugins) : 'None');
  
  // Check current user role
  const userRole = localStorage.getItem('userRole') || sessionStorage.getItem('userRole');
  console.log('2. Current user role:', userRole);
  
  // Check enabled plugins
  const plugins = getStoredPlugins();
  const enabledPlugins = plugins.filter(p => p.enabled);
  console.log('3. Enabled plugins:', enabledPlugins.map(p => ({ id: p.id, name: p.name, enabled: p.enabled })));
  
  // Check salary components plugin specifically
  const salaryPlugin = plugins.find(p => p.id === 'salary-components-plugin');
  console.log('4. Salary Components plugin:', salaryPlugin ? {
    id: salaryPlugin.id,
    name: salaryPlugin.name,
    enabled: salaryPlugin.enabled,
    menuCategories: salaryPlugin.menuCategories.length,
    firstMenuCategory: salaryPlugin.menuCategories[0]
  } : 'Not found');
  
  // Check role access for salary components
  if (salaryPlugin && salaryPlugin.menuCategories[0]) {
    const hasAccess = salaryPlugin.menuCategories[0].items.some(item => 
      item.roles.includes(userRole as any)
    );
    console.log('5. User has access to salary components:', hasAccess);
  }
  
  console.log('=== End Debug Information ===');
};

// Helper function to demonstrate plugin management in browser console
export const pluginDemo = {
  init: initializeDefaultPlugins,
  enable: enablePlugin,
  disable: disablePlugin,
  list: getStoredPlugins,
  clear: clearPlugins,
  forceReinit: forceReinitializePlugins,
  debug: debugPlugins,
  showInstructions: () => {
    console.log(`
Plugin System Demo Instructions:

1. Initialize default plugins:
   pluginDemo.init()

2. Enable a plugin:
   pluginDemo.enable('analytics-plugin')

3. Disable a plugin:
   pluginDemo.disable('analytics-plugin')

4. List all plugins:
   pluginDemo.list()

5. Clear all plugins:
   pluginDemo.clear()

6. Force reinitialize all plugins:
   pluginDemo.forceReinit()

7. Debug plugin information:
   pluginDemo.debug()

Note: Changes will be reflected in the sidebar after a page refresh.
    `);
  }
};

// Make demo available globally for testing
if (typeof window !== 'undefined') {
  (window as any).pluginDemo = pluginDemo;
  (window as any).debugPlugins = debugPlugins;
  (window as any).forceReinitializePlugins = forceReinitializePlugins;
  (window as any).clearPlugins = clearPlugins;
  (window as any).getStoredPlugins = getStoredPlugins;
} 