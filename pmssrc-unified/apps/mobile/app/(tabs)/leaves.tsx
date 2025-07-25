import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
} from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { useAuth } from '../../src/providers/AuthProvider';
import { LeaveService, LeaveBalance } from '../../src/modules/leaves/services/LeaveService';
import { LeaveRecord } from '@pmssrc/shared-types';
import { LeaveApplicationForm } from '../../src/modules/leaves/components/LeaveApplicationForm';
import { theme } from '../../src/styles/theme';

export default function LeavesScreen() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [leaveHistory, setLeaveHistory] = useState<LeaveRecord[]>([]);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance[]>([]);

  useEffect(() => {
    loadLeaveData();
  }, []);

  const loadLeaveData = async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      const [history, balance] = await Promise.all([
        LeaveService.getLeaveHistory(user.id),
        LeaveService.getLeaveBalance(user.id),
      ]);
      setLeaveHistory(history);
      setLeaveBalance(balance);
    } catch (error) {
      console.error('Failed to load leave data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelLeave = async (leaveId: string) => {
    Alert.alert(
      'Cancel Leave',
      'Are you sure you want to cancel this leave application?',
      [
        { text: 'No', style: 'cancel' },
        {
          text: 'Yes',
          style: 'destructive',
          onPress: async () => {
            try {
              await LeaveService.cancelLeave(leaveId);
              Alert.alert('Success', 'Leave application cancelled successfully');
              loadLeaveData();
            } catch (error) {
              Alert.alert('Error', 'Failed to cancel leave application');
            }
          },
        },
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return theme.colors.success;
      case 'rejected':
        return theme.colors.error;
      case 'pending':
        return theme.colors.warning;
      default:
        return theme.colors.text.secondary;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Leaves</Text>
        <Text style={styles.subtitle}>Manage your leave requests</Text>
      </View>

      {/* Leave Balance */}
      <View style={styles.balanceContainer}>
        <Text style={styles.sectionTitle}>Leave Balance</Text>
        <View style={styles.balanceGrid}>
          {leaveBalance.map((balance, index) => (
            <View key={index} style={styles.balanceCard}>
              <Text style={styles.balanceType}>
                {LeaveService.getLeaveTypeDisplayName(balance.leaveType)}
              </Text>
              <Text style={styles.balanceNumber}>{balance.availableLeaves}</Text>
              <Text style={styles.balanceLabel}>Available</Text>
              <Text style={styles.balanceUsed}>
                {balance.usedLeaves} used
              </Text>
            </View>
          ))}
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => setShowApplicationForm(true)}
        >
          <FontAwesome name="plus" size={20} color={theme.colors.primary} />
          <Text style={styles.actionButtonText}>Apply for Leave</Text>
        </TouchableOpacity>
      </View>

      {/* Leave History */}
      <View style={styles.historyContainer}>
        <Text style={styles.sectionTitle}>Leave History</Text>
        {leaveHistory.length === 0 ? (
          <View style={styles.emptyState}>
            <FontAwesome name="calendar-o" size={48} color={theme.colors.text.secondary} />
            <Text style={styles.emptyText}>No leave applications yet</Text>
            <Text style={styles.emptySubtext}>
              Apply for your first leave to see it here
            </Text>
          </View>
        ) : (
          leaveHistory.map((leave, index) => (
            <View key={index} style={styles.leaveCard}>
              <View style={styles.leaveHeader}>
                <View style={styles.leaveTypeContainer}>
                  <Text style={styles.leaveType}>
                    {LeaveService.getLeaveTypeDisplayName(leave.leaveType)}
                  </Text>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(leave.status) }]}>
                    <Text style={styles.statusText}>
                      {LeaveService.getLeaveStatusDisplayName(leave.status)}
                    </Text>
                  </View>
                </View>
                {leave.status === 'pending' && (
                  <TouchableOpacity
                    style={styles.cancelButton}
                    onPress={() => handleCancelLeave(leave.id)}
                  >
                    <FontAwesome name="times" size={16} color={theme.colors.error} />
                  </TouchableOpacity>
                )}
              </View>

              <View style={styles.leaveDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Duration:</Text>
                  <Text style={styles.detailValue}>
                    {formatDate(leave.startDate)} - {formatDate(leave.endDate)}
                    {leave.halfDay && ` (${leave.halfDayType} half day)`}
                  </Text>
                </View>

                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Reason:</Text>
                  <Text style={styles.detailValue}>{leave.reason}</Text>
                </View>

                {leave.comments && (
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Comments:</Text>
                    <Text style={styles.detailValue}>{leave.comments}</Text>
                  </View>
                )}
              </View>
            </View>
          ))
        )}
      </View>

      {/* Leave Application Modal */}
      <Modal
        visible={showApplicationForm}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <LeaveApplicationForm
          onSuccess={() => {
            setShowApplicationForm(false);
            loadLeaveData();
          }}
          onCancel={() => setShowApplicationForm(false)}
        />
      </Modal>
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
  balanceContainer: {
    padding: theme.spacing.xl,
  },
  sectionTitle: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
  },
  balanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  balanceCard: {
    width: '48%',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginBottom: theme.spacing.md,
    ...theme.shadows.sm,
  },
  balanceType: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xs,
  },
  balanceNumber: {
    fontSize: theme.typography.h2.fontSize,
    fontWeight: theme.typography.h2.fontWeight,
    color: theme.colors.primary,
  },
  balanceLabel: {
    fontSize: theme.typography.body2.fontSize,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.xs,
  },
  balanceUsed: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.xs,
  },
  actionsContainer: {
    padding: theme.spacing.xl,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    ...theme.shadows.sm,
  },
  actionButtonText: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    color: theme.colors.primary,
    marginLeft: theme.spacing.sm,
  },
  historyContainer: {
    padding: theme.spacing.xl,
  },
  emptyState: {
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  emptyText: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text.primary,
    marginTop: theme.spacing.md,
  },
  emptySubtext: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginTop: theme.spacing.sm,
  },
  leaveCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    ...theme.shadows.sm,
  },
  leaveHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  leaveTypeContainer: {
    flex: 1,
  },
  leaveType: {
    fontSize: theme.typography.h4.fontSize,
    fontWeight: theme.typography.h4.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.xs,
  },
  statusBadge: {
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
    borderRadius: theme.borderRadius.sm,
    alignSelf: 'flex-start',
  },
  statusText: {
    fontSize: theme.typography.caption.fontSize,
    fontWeight: '600',
    color: theme.colors.text.inverse,
  },
  cancelButton: {
    padding: theme.spacing.sm,
  },
  leaveDetails: {
    gap: theme.spacing.sm,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  detailLabel: {
    fontSize: theme.typography.body2.fontSize,
    fontWeight: '600',
    color: theme.colors.text.secondary,
    width: 80,
  },
  detailValue: {
    fontSize: theme.typography.body2.fontSize,
    color: theme.colors.text.primary,
    flex: 1,
  },
}); 