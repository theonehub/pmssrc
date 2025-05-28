# React Native Mobile App Setup Guide

## Project Initialization

```bash
# Create React Native project with TypeScript template
npx react-native init PMSMobile --template react-native-template-typescript

# Navigate to project directory
cd PMSMobile

# Install additional dependencies
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context
npm install react-native-paper react-native-vector-icons
npm install @react-native-async-storage/async-storage
npm install react-native-keychain
npm install react-native-image-picker
npm install react-native-document-picker
npm install react-native-date-picker
npm install react-native-chart-kit
npm install @react-native-community/push-notification-ios
npm install react-native-push-notification

# Development dependencies
npm install --save-dev @types/react-native-vector-icons
npm install --save-dev reactotron-react-native
```

## Project Structure

```
PMSMobile/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Common components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── forms/          # Form components
│   │   └── cards/          # Card components
│   ├── screens/            # Screen components
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   └── BiometricSetupScreen.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardScreen.tsx
│   │   ├── attendance/
│   │   │   ├── AttendanceScreen.tsx
│   │   │   ├── CheckInScreen.tsx
│   │   │   └── AttendanceHistoryScreen.tsx
│   │   ├── leaves/
│   │   │   ├── LeaveApplicationScreen.tsx
│   │   │   ├── LeaveHistoryScreen.tsx
│   │   │   └── LeaveBalanceScreen.tsx
│   │   ├── reimbursements/
│   │   │   ├── ReimbursementListScreen.tsx
│   │   │   └── CreateReimbursementScreen.tsx
│   │   └── profile/
│   │       ├── ProfileScreen.tsx
│   │       └── SettingsScreen.tsx
│   ├── navigation/         # Navigation configuration
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   ├── TabNavigator.tsx
│   │   └── types.ts
│   ├── services/           # API services (shared with web)
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   ├── attendanceService.ts
│   │   ├── leaveService.ts
│   │   └── reimbursementService.ts
│   ├── utils/              # Utility functions (shared with web)
│   │   ├── validation.ts
│   │   ├── dateUtils.ts
│   │   ├── storage.ts
│   │   └── biometric.ts
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useAttendance.ts
│   │   ├── useBiometric.ts
│   │   └── useNetworkStatus.ts
│   ├── context/            # React context providers
│   │   ├── AuthContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── NotificationContext.tsx
│   ├── types/              # TypeScript types (shared with web)
│   │   └── index.ts
│   ├── constants/          # App constants (shared with web)
│   │   └── index.ts
│   ├── assets/             # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   └── styles/             # Style definitions
│       ├── colors.ts
│       ├── typography.ts
│       └── spacing.ts
├── android/                # Android-specific code
├── ios/                    # iOS-specific code
├── __tests__/              # Test files
├── package.json
├── tsconfig.json
├── metro.config.js
└── react-native.config.js
```

## Key Implementation Examples

### 1. Authentication Screen with Biometric Support

```typescript
// src/screens/auth/LoginScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  TextInput,
  Button,
  Card,
  Title,
  Paragraph,
  ActivityIndicator,
} from 'react-native-paper';
import { useAuth } from '../../hooks/useAuth';
import { useBiometric } from '../../hooks/useBiometric';
import { validateEmail } from '../../utils/validation';
import { LoginCredentials } from '../../types';

const LoginScreen: React.FC = () => {
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { login } = useAuth();
  const { isBiometricAvailable, authenticateWithBiometric } = useBiometric();

  useEffect(() => {
    // Check if biometric authentication is available and user has it enabled
    checkBiometricLogin();
  }, []);

  const checkBiometricLogin = async () => {
    if (await isBiometricAvailable()) {
      // Show biometric prompt if user has previously logged in
      const hasStoredCredentials = await checkStoredCredentials();
      if (hasStoredCredentials) {
        showBiometricPrompt();
      }
    }
  };

  const showBiometricPrompt = async () => {
    try {
      const success = await authenticateWithBiometric();
      if (success) {
        // Auto-login with stored credentials
        await loginWithStoredCredentials();
      }
    } catch (error) {
      console.log('Biometric authentication cancelled');
    }
  };

  const handleLogin = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      await login(credentials);
      // Optionally save credentials for biometric login
      await promptForBiometricSetup();
    } catch (error) {
      Alert.alert('Login Failed', error.message);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!credentials.username) {
      newErrors.username = 'Username is required';
    } else if (!validateEmail(credentials.username)) {
      newErrors.username = 'Invalid email format';
    }

    if (!credentials.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Welcome Back</Title>
          <Paragraph style={styles.subtitle}>
            Sign in to your account
          </Paragraph>

          <TextInput
            label="Email"
            value={credentials.username}
            onChangeText={(text) =>
              setCredentials({ ...credentials, username: text })
            }
            error={!!errors.username}
            style={styles.input}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
          />
          {errors.username && (
            <Paragraph style={styles.errorText}>{errors.username}</Paragraph>
          )}

          <TextInput
            label="Password"
            value={credentials.password}
            onChangeText={(text) =>
              setCredentials({ ...credentials, password: text })
            }
            error={!!errors.password}
            secureTextEntry
            style={styles.input}
            autoComplete="password"
          />
          {errors.password && (
            <Paragraph style={styles.errorText}>{errors.password}</Paragraph>
          )}

          <Button
            mode="contained"
            onPress={handleLogin}
            loading={loading}
            disabled={loading}
            style={styles.loginButton}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </Button>

          {isBiometricAvailable && (
            <Button
              mode="outlined"
              onPress={showBiometricPrompt}
              style={styles.biometricButton}
              icon="fingerprint"
            >
              Use Biometric Login
            </Button>
          )}
        </Card.Content>
      </Card>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  card: {
    padding: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 24,
    opacity: 0.7,
  },
  input: {
    marginBottom: 8,
  },
  errorText: {
    color: '#d32f2f',
    fontSize: 12,
    marginBottom: 8,
  },
  loginButton: {
    marginTop: 16,
    marginBottom: 8,
  },
  biometricButton: {
    marginTop: 8,
  },
});

export default LoginScreen;
```

### 2. Attendance Check-in Screen with Location

```typescript
// src/screens/attendance/CheckInScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Surface,
  ActivityIndicator,
} from 'react-native-paper';
import Geolocation from '@react-native-community/geolocation';
import { useAttendance } from '../../hooks/useAttendance';
import { formatTime } from '../../utils/dateUtils';

interface Location {
  latitude: number;
  longitude: number;
}

const CheckInScreen: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [location, setLocation] = useState<Location | null>(null);
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);

  const { checkIn, checkOut, todayAttendance } = useAttendance();

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    requestLocationPermission();
  }, []);

  const requestLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Location Permission',
            message: 'This app needs access to location for attendance tracking.',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          }
        );
        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          getCurrentLocation();
        }
      } catch (err) {
        console.warn(err);
      }
    } else {
      getCurrentLocation();
    }
  };

  const getCurrentLocation = () => {
    setLocationLoading(true);
    Geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setLocationLoading(false);
      },
      (error) => {
        console.log(error);
        setLocationLoading(false);
        Alert.alert('Location Error', 'Unable to get current location');
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
    );
  };

  const handleCheckIn = async () => {
    if (!location) {
      Alert.alert('Location Required', 'Please enable location to check in');
      return;
    }

    setLoading(true);
    try {
      await checkIn({
        timestamp: new Date().toISOString(),
        location: location,
      });
      Alert.alert('Success', 'Checked in successfully!');
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    setLoading(true);
    try {
      await checkOut({
        timestamp: new Date().toISOString(),
        location: location,
      });
      Alert.alert('Success', 'Checked out successfully!');
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const isCheckedIn = todayAttendance?.check_in && !todayAttendance?.check_out;

  return (
    <View style={styles.container}>
      <Card style={styles.timeCard}>
        <Card.Content style={styles.timeContent}>
          <Title style={styles.timeText}>{formatTime(currentTime)}</Title>
          <Paragraph style={styles.dateText}>
            {currentTime.toLocaleDateString()}
          </Paragraph>
        </Card.Content>
      </Card>

      <Surface style={styles.statusCard}>
        <Title style={styles.statusTitle}>Today's Status</Title>
        {todayAttendance ? (
          <View>
            {todayAttendance.check_in && (
              <Paragraph>
                Check In: {formatTime(new Date(todayAttendance.check_in))}
              </Paragraph>
            )}
            {todayAttendance.check_out && (
              <Paragraph>
                Check Out: {formatTime(new Date(todayAttendance.check_out))}
              </Paragraph>
            )}
          </View>
        ) : (
          <Paragraph>No attendance record for today</Paragraph>
        )}
      </Surface>

      <View style={styles.locationContainer}>
        {locationLoading ? (
          <ActivityIndicator size="small" />
        ) : location ? (
          <Paragraph style={styles.locationText}>
            📍 Location detected
          </Paragraph>
        ) : (
          <Button onPress={getCurrentLocation} mode="outlined" compact>
            Enable Location
          </Button>
        )}
      </View>

      <View style={styles.buttonContainer}>
        {!isCheckedIn ? (
          <Button
            mode="contained"
            onPress={handleCheckIn}
            loading={loading}
            disabled={loading || !location}
            style={[styles.button, styles.checkInButton]}
            contentStyle={styles.buttonContent}
          >
            Check In
          </Button>
        ) : (
          <Button
            mode="contained"
            onPress={handleCheckOut}
            loading={loading}
            disabled={loading}
            style={[styles.button, styles.checkOutButton]}
            contentStyle={styles.buttonContent}
          >
            Check Out
          </Button>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  timeCard: {
    marginBottom: 16,
  },
  timeContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  timeText: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  dateText: {
    fontSize: 16,
    opacity: 0.7,
  },
  statusCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
  },
  statusTitle: {
    marginBottom: 8,
  },
  locationContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  locationText: {
    color: '#4caf50',
  },
  buttonContainer: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  button: {
    marginVertical: 8,
  },
  buttonContent: {
    paddingVertical: 8,
  },
  checkInButton: {
    backgroundColor: '#4caf50',
  },
  checkOutButton: {
    backgroundColor: '#f44336',
  },
});

export default CheckInScreen;
```

### 3. Navigation Configuration

```typescript
// src/navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useAuth } from '../hooks/useAuth';
import AuthNavigator from './AuthNavigator';
import TabNavigator from './TabNavigator';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Stack = createStackNavigator();

const AppNavigator: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <Stack.Screen name="Main" component={TabNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
```

### 4. Custom Hooks for Business Logic

```typescript
// src/hooks/useAttendance.ts
import { useState, useEffect } from 'react';
import { AttendanceRecord } from '../types';
import { attendanceService } from '../services/attendanceService';
import { useAuth } from './useAuth';

interface CheckInData {
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export const useAttendance = () => {
  const [todayAttendance, setTodayAttendance] = useState<AttendanceRecord | null>(null);
  const [attendanceHistory, setAttendanceHistory] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchTodayAttendance();
    }
  }, [user]);

  const fetchTodayAttendance = async () => {
    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      const attendance = await attendanceService.getAttendanceByDate(user!.emp_id, today);
      setTodayAttendance(attendance);
    } catch (error) {
      console.error('Error fetching today attendance:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkIn = async (data: CheckInData) => {
    try {
      const result = await attendanceService.checkIn({
        emp_id: user!.emp_id,
        timestamp: data.timestamp,
        location: data.location,
      });
      setTodayAttendance(result);
      return result;
    } catch (error) {
      throw error;
    }
  };

  const checkOut = async (data: CheckInData) => {
    try {
      const result = await attendanceService.checkOut({
        emp_id: user!.emp_id,
        timestamp: data.timestamp,
        location: data.location,
      });
      setTodayAttendance(result);
      return result;
    } catch (error) {
      throw error;
    }
  };

  const fetchAttendanceHistory = async (month?: number, year?: number) => {
    try {
      setLoading(true);
      const history = await attendanceService.getAttendanceHistory(
        user!.emp_id,
        month,
        year
      );
      setAttendanceHistory(history);
    } catch (error) {
      console.error('Error fetching attendance history:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    todayAttendance,
    attendanceHistory,
    loading,
    checkIn,
    checkOut,
    fetchTodayAttendance,
    fetchAttendanceHistory,
  };
};
```

## Platform-Specific Features

### iOS Configuration

```xml
<!-- ios/PMSMobile/Info.plist -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access for attendance tracking</string>
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to capture receipts</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs photo library access to select images</string>
<key>NSFaceIDUsageDescription</key>
<string>This app uses Face ID for secure authentication</string>
```

### Android Configuration

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.USE_FINGERPRINT" />
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
```

## Development Scripts

```json
{
  "scripts": {
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "start": "react-native start",
    "test": "jest",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "build:android": "cd android && ./gradlew assembleRelease",
    "build:ios": "react-native run-ios --configuration Release"
  }
}
```

This React Native setup provides:

1. **Native Performance**: True native app performance
2. **Device Features**: Camera, location, biometric authentication
3. **Offline Support**: Local storage and sync capabilities
4. **Push Notifications**: Real-time updates
5. **Shared Business Logic**: Reuse validation and API services from web app
6. **Type Safety**: Full TypeScript support
7. **Modern UI**: Material Design with React Native Paper

The mobile app complements the web application while providing a superior mobile user experience with native device integration. 