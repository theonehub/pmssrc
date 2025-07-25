import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { useAuth } from '../../src/providers/AuthProvider';
import { LocationService } from '../../src/modules/location/services/LocationService';
import { attendanceService } from '../../src/modules/attendance/services/AttendanceService';
import { AttendanceRecord } from '@pmssrc/shared-types';
import { theme } from '../../src/styles/theme';

export default function AttendanceScreen() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState<any>(null);
  const [isWithinOffice, setIsWithinOffice] = useState(false);
  const [todayAttendance, setTodayAttendance] = useState<AttendanceRecord | null>(null);

  useEffect(() => {
    checkCurrentLocation();
    loadTodayAttendance();
  }, []);

  const checkCurrentLocation = async () => {
    try {
      const location = await LocationService.getCurrentPosition();
      setCurrentLocation(location);
      
      const geofenceCheck = await LocationService.isWithinOfficeGeofence();
      setIsWithinOffice(geofenceCheck.isWithin);
    } catch (error) {
      console.error('Failed to get location:', error);
    }
  };

  const loadTodayAttendance = async () => {
    if (!user) return;
    
    try {
      const attendance = await attendanceService.getTodayAttendance();
      setTodayAttendance(attendance);
    } catch (error) {
      console.error('Failed to load attendance:', error);
    }
  };

  const handleCheckIn = async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      
      // Get current location
      const location = await LocationService.getCurrentPosition();
      
      // Check if within office geofence
      const geofenceCheck = await LocationService.isWithinOfficeGeofence();
      if (!geofenceCheck.isWithin) {
        Alert.alert(
          'Location Error',
          'You must be within office premises to check in. Please ensure you are at the office location.',
          [{ text: 'OK' }]
        );
        return;
      }

      // Check location accuracy
      if (!LocationService.isLocationAccurate(location)) {
        Alert.alert(
          'Location Accuracy',
          'Your location accuracy is low. Please ensure GPS is enabled and try again.',
          [{ text: 'OK' }]
        );
        return;
      }

      // Perform check-in
      const attendanceRecord = await attendanceService.checkIn(location);
      setTodayAttendance(attendanceRecord);
      Alert.alert('Success', 'Check-in successful!');
    } catch (error) {
      Alert.alert('Check-in Failed', error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckOut = async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      
      // Get current location
      const location = await LocationService.getCurrentPosition();
      
      // Perform check-out
      const attendanceRecord = await attendanceService.checkOut(location);
      setTodayAttendance(attendanceRecord);
      Alert.alert('Success', 'Check-out successful!');
    } catch (error) {
      Alert.alert('Check-out Failed', error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const attendanceStatus = attendanceService.getAttendanceStatus(todayAttendance);
  const canCheckIn = attendanceStatus === 'NOT_CHECKED_IN';
  const canCheckOut = attendanceStatus === 'CHECKED_IN';

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Attendance</Text>
        <Text style={styles.subtitle}>Track your work hours</Text>
      </View>

      <View style={styles.locationCard}>
        <Text style={styles.cardTitle}>Location Status</Text>
        <View style={styles.locationInfo}>
          <FontAwesome 
            name={isWithinOffice ? 'check-circle' : 'times-circle'} 
            size={20} 
            color={isWithinOffice ? theme.colors.success : theme.colors.error} 
          />
          <Text style={[styles.locationText, { color: isWithinOffice ? theme.colors.success : theme.colors.error }]}>
            {isWithinOffice ? 'Within Office' : 'Outside Office'}
          </Text>
        </View>
        {currentLocation && (
          <Text style={styles.locationDetails}>
            Lat: {currentLocation.latitude.toFixed(4)}, Long: {currentLocation.longitude.toFixed(4)}
          </Text>
        )}
      </View>

      <View style={styles.attendanceCard}>
        <Text style={styles.cardTitle}>Today's Attendance</Text>
        
        {todayAttendance ? (
          <View style={styles.attendanceInfo}>
            <View style={styles.attendanceRow}>
              <Text style={styles.attendanceLabel}>Check-in:</Text>
              <Text style={styles.attendanceValue}>
                {todayAttendance.check_in_time ? attendanceService.formatTime(todayAttendance.check_in_time) : 'Not checked in'}
              </Text>
            </View>
            <View style={styles.attendanceRow}>
              <Text style={styles.attendanceLabel}>Check-out:</Text>
              <Text style={styles.attendanceValue}>
                {todayAttendance.check_out_time ? attendanceService.formatTime(todayAttendance.check_out_time) : 'Not checked out'}
              </Text>
            </View>
            <View style={styles.attendanceRow}>
              <Text style={styles.attendanceLabel}>Status:</Text>
              <Text style={[styles.attendanceValue, { color: theme.colors.primary }]}>
                {todayAttendance.status}
              </Text>
            </View>
            {todayAttendance.check_in_time && todayAttendance.check_out_time && (
              <View style={styles.attendanceRow}>
                <Text style={styles.attendanceLabel}>Working Hours:</Text>
                <Text style={styles.attendanceValue}>
                  {attendanceService.getWorkingHours(todayAttendance)} hours
                </Text>
              </View>
            )}
          </View>
        ) : (
          <Text style={styles.noAttendance}>No attendance record for today</Text>
        )}
      </View>

      <View style={styles.actionsContainer}>
        {canCheckIn && (
          <TouchableOpacity
            style={[styles.actionButton, styles.checkInButton, isLoading && styles.buttonDisabled]}
            onPress={handleCheckIn}
            disabled={isLoading || !isWithinOffice}
          >
            <FontAwesome name="sign-in" size={20} color="white" />
            <Text style={styles.actionButtonText}>
              {isLoading ? 'Checking In...' : 'Check In'}
            </Text>
          </TouchableOpacity>
        )}

        {canCheckOut && (
          <TouchableOpacity
            style={[styles.actionButton, styles.checkOutButton, isLoading && styles.buttonDisabled]}
            onPress={handleCheckOut}
            disabled={isLoading}
          >
            <FontAwesome name="sign-out" size={20} color="white" />
            <Text style={styles.actionButtonText}>
              {isLoading ? 'Checking Out...' : 'Check Out'}
            </Text>
          </TouchableOpacity>
        )}

        {!canCheckIn && !canCheckOut && (
          <Text style={styles.completedMessage}>Attendance completed for today</Text>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.primary,
  },
  title: {
    fontSize: theme.typography.h1.fontSize,
    fontWeight: theme.typography.h1.fontWeight,
    color: theme.colors.text.inverse,
  },
  subtitle: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.inverse,
    opacity: 0.8,
    marginTop: theme.spacing.xs,
  },
  locationCard: {
    margin: theme.spacing.xl,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    ...theme.shadows.sm,
  },
  cardTitle: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  locationText: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    marginLeft: theme.spacing.sm,
  },
  locationDetails: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text.secondary,
  },
  attendanceCard: {
    margin: theme.spacing.xl,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    ...theme.shadows.sm,
  },
  attendanceInfo: {
    gap: theme.spacing.sm,
  },
  attendanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  attendanceLabel: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.secondary,
  },
  attendanceValue: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    color: theme.colors.text.primary,
  },
  noAttendance: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.secondary,
    fontStyle: 'italic',
  },
  actionsContainer: {
    padding: theme.spacing.xl,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.lg,
    marginBottom: theme.spacing.md,
    ...theme.shadows.sm,
  },
  checkInButton: {
    backgroundColor: theme.colors.success,
  },
  checkOutButton: {
    backgroundColor: theme.colors.warning,
  },
  buttonDisabled: {
    backgroundColor: theme.colors.disabled,
  },
  actionButtonText: {
    color: theme.colors.text.inverse,
    fontSize: theme.typography.button.fontSize,
    fontWeight: theme.typography.button.fontWeight,
    marginLeft: theme.spacing.sm,
  },
  completedMessage: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.success,
    textAlign: 'center',
    fontStyle: 'italic',
  },
}); 