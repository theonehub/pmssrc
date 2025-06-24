import { clearPlugins, initializeDefaultPlugins } from './pluginInitializer';

export const clearAndReinitializePlugins = () => {
  console.log('Clearing existing plugins...');
  clearPlugins();
  
  console.log('Reinitializing plugins with updated configuration...');
  initializeDefaultPlugins();
  
  console.log('Plugins reinitialized successfully!');
  console.log('Please refresh the page to see the updated menu items.');
};

// Auto-execute when imported
clearAndReinitializePlugins(); 