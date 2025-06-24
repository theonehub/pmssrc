import { useState, useEffect, useCallback } from 'react';
import { PluginConfigRuntime } from '../shared/types/plugin';
import { pluginService } from '../shared/services/pluginService';

interface UsePluginsReturn {
  plugins: PluginConfigRuntime[];
  enabledPlugins: PluginConfigRuntime[];
  loading: boolean;
  error: string | null;
  isPluginEnabled: (pluginId: string) => boolean;
  refreshPlugins: () => Promise<void>;
}

export const usePlugins = (): UsePluginsReturn => {
  const [plugins, setPlugins] = useState<PluginConfigRuntime[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPlugins = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      await pluginService.initializePlugins();
      const availablePlugins = pluginService.getAvailablePlugins();
      setPlugins(availablePlugins);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load plugins';
      setError(errorMessage);
      console.error('Plugin loading error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshPlugins = useCallback(async () => {
    await loadPlugins();
  }, [loadPlugins]);

  const isPluginEnabled = useCallback((pluginId: string): boolean => {
    return pluginService.isPluginEnabled(pluginId);
  }, []);

  const enabledPlugins = plugins.filter(plugin => plugin.enabled);

  useEffect(() => {
    loadPlugins();
  }, [loadPlugins]);

  return {
    plugins,
    enabledPlugins,
    loading,
    error,
    isPluginEnabled,
    refreshPlugins,
  };
}; 