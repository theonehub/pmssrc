import { PluginConfig, PluginConfigRuntime, PluginRegistry, PluginLoader } from '../types/plugin';
import { getIcon } from './iconService';

class PluginService implements PluginLoader {
  private registry: PluginRegistry = {};
  private discoveryStrategies: PluginDiscoveryStrategy[] = [];

  constructor() {
    // Initialize with different discovery strategies
    this.discoveryStrategies = [
      new LocalStorageDiscovery(),
      new ManifestDiscovery(),
      new APIDiscovery(),
      new FileSystemDiscovery(),
      new ConfigDiscovery()
    ];
  }

  // Convert plugin config with string icons to runtime config with React elements
  private convertToRuntime(plugin: PluginConfig): PluginConfigRuntime {
    return {
      ...plugin,
      menuCategories: plugin.menuCategories.map(category => ({
        ...category,
        icon: getIcon(category.icon),
        items: category.items.map(item => ({
          ...item,
          icon: getIcon(item.icon),
        })),
      })),
    };
  }

  async initializePlugins(): Promise<void> {
    try {
      // Discover and load plugins from all strategies
      for (const strategy of this.discoveryStrategies) {
        const plugins = await strategy.discoverPlugins();
        plugins.forEach(plugin => {
          if (plugin.enabled) {
            this.registerPlugin(plugin);
          }
        });
      }
    } catch (error) {
      console.error('Failed to initialize plugins:', error);
    }
  }

  async loadPlugin(pluginId: string): Promise<PluginConfig | null> {
    try {
      // Try each discovery strategy to find the plugin
      for (const strategy of this.discoveryStrategies) {
        const plugin = await strategy.loadPlugin(pluginId);
        if (plugin) {
          return plugin;
        }
      }
      return null;
    } catch (error) {
      console.error(`Failed to load plugin ${pluginId}:`, error);
      return null;
    }
  }

  registerPlugin(plugin: PluginConfig): void {
    if (this.validatePlugin(plugin)) {
      const runtimePlugin = this.convertToRuntime(plugin);
      this.registry[plugin.id] = runtimePlugin;
      console.log(`Plugin registered: ${plugin.name} (${plugin.id})`);
    } else {
      console.error(`Invalid plugin configuration: ${plugin.id}`);
    }
  }

  unregisterPlugin(pluginId: string): void {
    delete this.registry[pluginId];
    console.log(`Plugin unregistered: ${pluginId}`);
  }

  getAvailablePlugins(): PluginConfigRuntime[] {
    return Object.values(this.registry);
  }

  getEnabledPlugins(): PluginConfigRuntime[] {
    return Object.values(this.registry).filter(plugin => plugin.enabled);
  }

  isPluginEnabled(pluginId: string): boolean {
    return this.registry[pluginId]?.enabled || false;
  }

  private validatePlugin(plugin: PluginConfig): boolean {
    return !!(
      plugin.id &&
      plugin.name &&
      plugin.version &&
      plugin.menuCategories &&
      Array.isArray(plugin.menuCategories)
    );
  }
}

// Abstract base class for plugin discovery strategies
abstract class PluginDiscoveryStrategy {
  abstract discoverPlugins(): Promise<PluginConfig[]>;
  abstract loadPlugin(pluginId: string): Promise<PluginConfig | null>;
}

// Strategy 1: LocalStorage-based discovery
class LocalStorageDiscovery extends PluginDiscoveryStrategy {
  async discoverPlugins(): Promise<PluginConfig[]> {
    try {
      const pluginsData = localStorage.getItem('pms_plugins');
      if (pluginsData) {
        return JSON.parse(pluginsData);
      }
    } catch (error) {
      console.error('LocalStorage plugin discovery failed:', error);
    }
    return [];
  }

  async loadPlugin(pluginId: string): Promise<PluginConfig | null> {
    const plugins = await this.discoverPlugins();
    return plugins.find(plugin => plugin.id === pluginId) || null;
  }
}

// Strategy 2: Manifest file discovery
class ManifestDiscovery extends PluginDiscoveryStrategy {
  async discoverPlugins(): Promise<PluginConfig[]> {
    try {
      const response = await fetch('/plugins/manifest.json');
      if (response.ok) {
        const manifest = await response.json();
        return manifest.plugins || [];
      }
    } catch (error) {
      console.error('Manifest plugin discovery failed:', error);
    }
    return [];
  }

  async loadPlugin(pluginId: string): Promise<PluginConfig | null> {
    try {
      const response = await fetch(`/plugins/${pluginId}/plugin.json`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error(`Failed to load plugin ${pluginId} from manifest:`, error);
    }
    return null;
  }
}

// Strategy 3: API-based discovery
class APIDiscovery extends PluginDiscoveryStrategy {
  async discoverPlugins(): Promise<PluginConfig[]> {
    try {
      const response = await fetch('/api/v2/plugins');
      if (response.ok) {
        const data = await response.json();
        return data.plugins || [];
      }
    } catch (error) {
      console.error('API plugin discovery failed:', error);
    }
    return [];
  }

  async loadPlugin(pluginId: string): Promise<PluginConfig | null> {
    try {
      const response = await fetch(`/api/v2/plugins/${pluginId}`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error(`Failed to load plugin ${pluginId} from API:`, error);
    }
    return null;
  }
}

// Strategy 4: File system discovery (for development)
class FileSystemDiscovery extends PluginDiscoveryStrategy {
  async discoverPlugins(): Promise<PluginConfig[]> {
    try {
      // For Create React App, we'll use dynamic imports with known plugin paths
      const pluginIds = ['analytics-plugin', 'inventory-plugin', 'salary-components-plugin'];
      const plugins: PluginConfig[] = [];
      
      for (const pluginId of pluginIds) {
        try {
          // Dynamic import for known plugins
          const module = await import(`../../plugins/${pluginId}/plugin.config.ts`);
          if (module && module.default) {
            plugins.push(module.default);
          }
        } catch (error) {
          // Plugin doesn't exist or failed to load - this is expected
          console.debug(`Plugin ${pluginId} not found or failed to load`);
        }
      }
      
      return plugins;
    } catch (error) {
      console.error('FileSystem plugin discovery failed:', error);
    }
    return [];
  }

  async loadPlugin(pluginId: string): Promise<PluginConfig | null> {
    try {
      const module = await import(`../../plugins/${pluginId}/plugin.config.ts`);
      if (module && module.default) {
        return module.default;
      }
    } catch (error) {
      console.debug(`Plugin ${pluginId} not found or failed to load`);
    }
    return null;
  }
}

// Strategy 5: Static configuration discovery
class ConfigDiscovery extends PluginDiscoveryStrategy {
  async discoverPlugins(): Promise<PluginConfig[]> {
    // This could be loaded from environment variables or build-time configuration
    const staticPlugins = process.env.REACT_APP_PLUGINS;
    if (staticPlugins) {
      try {
        return JSON.parse(staticPlugins);
      } catch (error) {
        console.error('Static config plugin discovery failed:', error);
      }
    }
    return [];
  }

  async loadPlugin(pluginId: string): Promise<PluginConfig | null> {
    const plugins = await this.discoverPlugins();
    return plugins.find(plugin => plugin.id === pluginId) || null;
  }
}

// Export singleton instance
export const pluginService = new PluginService();
export default pluginService; 