import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useAuth } from '../../src/providers/AuthProvider';
import { theme } from '../../src/styles/theme';

export default function DashboardScreen() {
  const { user } = useAuth();

  const dashboardItems = [
    {
      title: 'Check In',
      icon: 'sign-in',
      color: theme.colors.success,
      onPress: () => {
        router.push('/(tabs)/attendance');
      },
    },
    {
      title: 'Apply Leave',
      icon: 'calendar-plus-o',
      color: theme.colors.info,
      onPress: () => {
        router.push('/(tabs)/leaves');
      },
    },
    {
      title: 'Submit Expense',
      icon: 'credit-card',
      color: theme.colors.warning,
      onPress: () => {
        router.push('/(tabs)/reimbursements');
      },
    },
    {
      title: 'Tax Calculator',
      icon: 'calculator',
      color: theme.colors.secondary,
      onPress: () => {
        router.push('/(tabs)/taxation');
      },
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.welcomeText}>Welcome back,</Text>
        <Text style={styles.userName}>{user?.first_name} {user?.last_name}</Text>
        <Text style={styles.userRole}>{user?.role}</Text>
      </View>

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.grid}>
          {dashboardItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.gridItem}
              onPress={item.onPress}
            >
              <View style={[styles.iconContainer, { backgroundColor: item.color }]}>
                <FontAwesome name={item.icon as any} size={24} color="white" />
              </View>
              <Text style={styles.gridItemText}>{item.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>Today's Summary</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>8</Text>
            <Text style={styles.statLabel}>Hours Worked</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>2</Text>
            <Text style={styles.statLabel}>Pending Leaves</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>₹5,000</Text>
            <Text style={styles.statLabel}>Pending Expenses</Text>
          </View>
        </View>
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
  welcomeText: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.inverse,
    opacity: 0.8,
  },
  userName: {
    fontSize: theme.typography.h2.fontSize,
    fontWeight: theme.typography.h2.fontWeight,
    color: theme.colors.text.inverse,
    marginTop: theme.spacing.xs,
  },
  userRole: {
    fontSize: theme.typography.body2.fontSize,
    color: theme.colors.text.inverse,
    opacity: 0.8,
    marginTop: theme.spacing.xs,
  },
  quickActions: {
    padding: theme.spacing.xl,
  },
  sectionTitle: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  gridItem: {
    width: '48%',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginBottom: theme.spacing.md,
    ...theme.shadows.sm,
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: theme.borderRadius.round,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  gridItemText: {
    fontSize: theme.typography.body2.fontSize,
    fontWeight: '600',
    color: theme.colors.text.primary,
    textAlign: 'center',
  },
  statsContainer: {
    padding: theme.spacing.xl,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginHorizontal: theme.spacing.xs,
    ...theme.shadows.sm,
  },
  statNumber: {
    fontSize: theme.typography.h2.fontSize,
    fontWeight: theme.typography.h2.fontWeight,
    color: theme.colors.primary,
  },
  statLabel: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginTop: theme.spacing.xs,
  },
});
