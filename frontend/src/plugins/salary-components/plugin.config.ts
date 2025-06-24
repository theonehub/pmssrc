import { PluginConfig } from '../../shared/types/plugin';

const salaryComponentsPlugin: PluginConfig = {
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
      priority: 8, // Between payouts and taxation
      items: [
        {
          title: 'Components List',
          icon: 'ListIcon',
          path: '/salary-components',
          roles: ['admin', 'superadmin', 'hr'],
        },
        {
          title: 'Create Component',
          icon: 'AddIcon',
          path: '/salary-components/create',
          roles: ['admin', 'superadmin'],
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
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'Employee Mapping',
          icon: 'PersonPinIcon',
          path: '/salary-components/employee-mapping',
          roles: ['admin', 'superadmin', 'hr'],
        },
      ],
    },
  ],
  dependencies: [],
  permissions: ['salary.read', 'salary.write', 'salary.manage'],
};

export default salaryComponentsPlugin; 