import NetInfo from '@react-native-community/netinfo';

export class NetworkService {
  /**
   * Check if device has internet connection
   */
  static async checkInternetConnection(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.isConnected === true && state.isInternetReachable === true;
    } catch (error) {
      console.error('Failed to check internet connection:', error);
      return false;
    }
  }

  /**
   * Require internet connection - throws error if not available
   */
  static async requireInternetConnection(): Promise<void> {
    const isConnected = await this.checkInternetConnection();
    if (!isConnected) {
      throw new Error('Internet connection required. Please check your network and try again.');
    }
  }

  /**
   * Wrapper for API calls to ensure internet connection
   */
  static async withInternetCheck<T>(apiCall: () => Promise<T>): Promise<T> {
    await this.requireInternetConnection();
    return apiCall();
  }

  /**
   * Monitor network state changes
   */
  static subscribeToNetworkChanges(callback: (isConnected: boolean) => void): () => void {
    return NetInfo.addEventListener(state => {
      const isConnected = state.isConnected === true && state.isInternetReachable === true;
      callback(isConnected);
    });
  }

  /**
   * Get current network state
   */
  static async getNetworkState(): Promise<{
    isConnected: boolean;
    isInternetReachable: boolean;
    type: string;
    isWifi: boolean;
    isCellular: boolean;
  }> {
    const state = await NetInfo.fetch();
    return {
      isConnected: state.isConnected === true,
      isInternetReachable: state.isInternetReachable === true,
      type: state.type,
      isWifi: state.type === 'wifi',
      isCellular: state.type === 'cellular',
    };
  }
} 