import * as Location from 'expo-location';
import { LocationData } from '@pmssrc/shared-types';
import { LocationValidator } from '@pmssrc/business-logic';

export interface OfficeLocation {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  geofenceRadius: number;
}

export interface LocationTrackingConfig {
  accuracy: Location.Accuracy;
  timeInterval: number;
  distanceInterval: number;
}

export class LocationService {
  private static locationSubscription: Location.LocationSubscription | null = null;
  private static geofenceRegions: Location.GeofenceRegion[] = [];
  private static officeLocations: OfficeLocation[] = [];

  /**
   * Request location permissions
   */
  static async requestPermissions(): Promise<boolean> {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      return false;
    }

    const backgroundStatus = await Location.requestBackgroundPermissionsAsync();
    return backgroundStatus.status === 'granted';
  }

  /**
   * Get current position
   */
  static async getCurrentPosition(): Promise<LocationData> {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      throw new Error('Location permission denied');
    }

    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
      timeInterval: 5000,
    });

    return {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      accuracy: location.coords.accuracy || 0,
      timestamp: location.timestamp,
    };
  }

  /**
   * Start real-time location tracking
   */
  static async startLocationTracking(
    onLocationUpdate: (location: LocationData) => void,
    onGeofenceEnter?: (region: Location.GeofenceRegion) => void,
    onGeofenceExit?: (region: Location.GeofenceRegion) => void,
    config?: Partial<LocationTrackingConfig>
  ): Promise<void> {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      throw new Error('Location permission denied');
    }

    const defaultConfig: LocationTrackingConfig = {
      accuracy: Location.Accuracy.High,
      timeInterval: 10000, // Update every 10 seconds
      distanceInterval: 10, // Update when moved 10 meters
    };

    const finalConfig = { ...defaultConfig, ...config };

    // Start real-time location tracking
    this.locationSubscription = await Location.watchPositionAsync(
      {
        accuracy: finalConfig.accuracy,
        timeInterval: finalConfig.timeInterval,
        distanceInterval: finalConfig.distanceInterval,
      },
      (location) => {
        const locationData: LocationData = {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          accuracy: location.coords.accuracy || 0,
          timestamp: location.timestamp,
        };
        onLocationUpdate(locationData);
      }
    );

    // Set up geofencing for office locations
    await this.setupGeofencing(onGeofenceEnter, onGeofenceExit);
  }

  /**
   * Set up geofencing for office locations
   */
  static async setupGeofencing(
    onEnter?: (region: Location.GeofenceRegion) => void,
    onExit?: (region: Location.GeofenceRegion) => void
  ): Promise<void> {
    try {
      // Get office locations from backend (you'll need to implement this)
      // For now, we'll use mock data
      this.officeLocations = [
        {
          id: 'office-1',
          name: 'Main Office',
          latitude: 40.7128,
          longitude: -74.0060,
          geofenceRadius: 100,
        },
        {
          id: 'office-2',
          name: 'Branch Office',
          latitude: 40.7589,
          longitude: -73.9851,
          geofenceRadius: 150,
        },
      ];

      this.geofenceRegions = this.officeLocations.map(office => ({
        identifier: office.id,
        latitude: office.latitude,
        longitude: office.longitude,
        radius: office.geofenceRadius,
        notifyOnEntry: true,
        notifyOnExit: true,
      }));

      // Start geofencing monitoring
      await Location.startGeofencingAsync(
        this.geofenceRegions,
        (event) => {
          if (event.type === Location.GeofencingEventType.Enter) {
            onEnter?.(event.region);
          } else if (event.type === Location.GeofencingEventType.Exit) {
            onExit?.(event.region);
          }
        }
      );
    } catch (error) {
      console.error('Failed to setup geofencing:', error);
    }
  }

  /**
   * Check if current location is within any office geofence
   */
  static async isWithinOfficeGeofence(): Promise<{ isWithin: boolean; office?: OfficeLocation }> {
    try {
      const currentLocation = await this.getCurrentPosition();
      
      for (const office of this.officeLocations) {
        const isWithin = LocationValidator.isWithinOfficeGeofence(
          currentLocation,
          { latitude: office.latitude, longitude: office.longitude },
          office.geofenceRadius
        );
        
        if (isWithin) {
          return { isWithin: true, office };
        }
      }
      
      return { isWithin: false };
    } catch (error) {
      console.error('Failed to check geofence:', error);
      return { isWithin: false };
    }
  }

  /**
   * Get nearest office location
   */
  static async getNearestOffice(): Promise<OfficeLocation | null> {
    try {
      const currentLocation = await this.getCurrentPosition();
      let nearestOffice: OfficeLocation | null = null;
      let shortestDistance = Infinity;

      for (const office of this.officeLocations) {
        const distance = LocationValidator.calculateDistance(
          currentLocation,
          { latitude: office.latitude, longitude: office.longitude }
        );

        if (distance < shortestDistance) {
          shortestDistance = distance;
          nearestOffice = office;
        }
      }

      return nearestOffice;
    } catch (error) {
      console.error('Failed to get nearest office:', error);
      return null;
    }
  }

  /**
   * Validate location accuracy
   */
  static isLocationAccurate(location: LocationData, requiredAccuracy: number = 10): boolean {
    return LocationValidator.isLocationAccurate(location, requiredAccuracy);
  }

  /**
   * Stop location tracking
   */
  static stopLocationTracking(): void {
    if (this.locationSubscription) {
      this.locationSubscription.remove();
      this.locationSubscription = null;
    }
  }

  /**
   * Get office locations
   */
  static getOfficeLocations(): OfficeLocation[] {
    return [...this.officeLocations];
  }

  /**
   * Add office location
   */
  static addOfficeLocation(office: OfficeLocation): void {
    this.officeLocations.push(office);
  }

  /**
   * Remove office location
   */
  static removeOfficeLocation(officeId: string): void {
    this.officeLocations = this.officeLocations.filter(office => office.id !== officeId);
  }
} 