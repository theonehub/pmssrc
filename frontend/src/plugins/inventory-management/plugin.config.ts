import { PluginConfig } from '../../shared/types/plugin';

const inventoryPlugin: PluginConfig = {
  id: 'inventory-plugin',
  name: 'Inventory Management',
  version: '2.1.0',
  description: 'Complete inventory management system',
  enabled: false, // This plugin is disabled, so it won't show in the menu
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
        {
          title: 'Shipping & Tracking',
          icon: 'ShippingIcon',
          path: '/shipping',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'QR Code Scanner',
          icon: 'QrCodeIcon',
          action: 'qr-scanner',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
      ],
    },
  ],
  dependencies: ['camera-access'],
  permissions: ['inventory.read', 'inventory.write'],
};

export default inventoryPlugin; 