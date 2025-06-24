import { ReactElement } from 'react';
import { UserRole } from './index';

export interface PluginMenuItem {
  title: string;
  icon: string; // Changed to string for icon name
  path?: string;
  action?: string;
  roles: UserRole[];
}

export interface PluginMenuCategory {
  id: string;
  title: string;
  icon: string; // Changed to string for icon name
  items: PluginMenuItem[];
  priority?: number; // For ordering plugins in the menu
}

export interface PluginConfig {
  id: string;
  name: string;
  version: string;
  description?: string;
  enabled: boolean;
  menuCategories: PluginMenuCategory[];
  dependencies?: string[];
  permissions?: string[];
}

// Runtime interfaces with actual React elements
export interface PluginMenuItemRuntime {
  title: string;
  icon: ReactElement;
  path?: string;
  action?: string;
  roles: UserRole[];
}

export interface PluginMenuCategoryRuntime {
  id: string;
  title: string;
  icon: ReactElement;
  items: PluginMenuItemRuntime[];
  priority?: number;
}

export interface PluginConfigRuntime {
  id: string;
  name: string;
  version: string;
  description?: string;
  enabled: boolean;
  menuCategories: PluginMenuCategoryRuntime[];
  dependencies?: string[];
  permissions?: string[];
}

export interface PluginRegistry {
  [pluginId: string]: PluginConfigRuntime;
}

export interface PluginLoader {
  loadPlugin: (pluginId: string) => Promise<PluginConfig | null>;
  registerPlugin: (plugin: PluginConfig) => void;
  unregisterPlugin: (pluginId: string) => void;
  getAvailablePlugins: () => PluginConfigRuntime[];
  getEnabledPlugins: () => PluginConfigRuntime[];
  isPluginEnabled: (pluginId: string) => boolean;
} 