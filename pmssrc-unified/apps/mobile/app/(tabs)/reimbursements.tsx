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
import { ReimbursementService, ReimbursementStats } from '../../src/modules/reimbursements/services/ReimbursementService';
import { ReimbursementRecord } from '@pmssrc/shared-types';
import { ReimbursementForm } from '../../src/modules/reimbursements/components/ReimbursementForm';
import { theme } from '../../src/styles/theme';

export default function ReimbursementsScreen() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [reimbursementHistory, setReimbursementHistory] = useState<ReimbursementRecord[]>([]);
  const [stats, setStats] = useState<ReimbursementStats | null>(null);

  useEffect(() => {
    loadReimbursementData();
  }, []);

  const loadReimbursementData = async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      const [history, statistics] = await Promise.all([
        ReimbursementService.getReimbursementHistory(user.id),
        ReimbursementService.getReimbursementStats(user.id),
      ]);
      setReimbursementHistory(history);
      setStats(statistics);
    } catch (error) {
      console.error('Failed to load reimbursement data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelReimbursement = async (reimbursementId: string) => {
    Alert.alert(
      'Cancel Reimbursement',
      'Are you sure you want to cancel this reimbursement request?',
      [
        { text: 'No', style: 'cancel' },
        {
          text: 'Yes',
          style: 'destructive',
          onPress: async () => {
            try {
              await ReimbursementService.cancelReimbursement(reimbursementId);
              Alert.alert('Success', 'Reimbursement request cancelled successfully');
              loadReimbursementData();
            } catch (error) {
              Alert.alert('Error', 'Failed to cancel reimbursement request');
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
        <Text style={styles.title}>Expenses</Text>
        <Text style={styles.subtitle}>Manage your reimbursement requests</Text>
      </View>

      {/* Statistics */}
      {stats && (
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.totalSubmitted}</Text>
              <Text style={styles.statLabel}>Submitted</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.totalApproved}</Text>
              <Text style={styles.statLabel}>Approved</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.totalPending}</Text>
              <Text style={styles.statLabel}>Pending</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.totalRejected}</Text>
              <Text style={styles.statLabel}>Rejected</Text>
            </View>
          </View>
          
          <View style={styles.totalAmountCard}>
            <Text style={styles.totalAmountLabel}>Total Approved Amount</Text>
            <Text style={styles.totalAmountValue}>
              {ReimbursementService.formatCurrency(stats.totalAmount)}
            </Text>
          </View>
        </View>
      )}

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => setShowApplicationForm(true)}
        >
          <FontAwesome name="plus" size={20} color={theme.colors.primary} />
          <Text style={styles.actionButtonText}>Submit Expense</Text>
        </TouchableOpacity>
      </View>

      {/* Reimbursement History */}
      <View style={styles.historyContainer}>
        <Text style={styles.sectionTitle}>Recent Requests</Text>
        {reimbursementHistory.length === 0 ? (
          <View style={styles.emptyState}>
            <FontAwesome name="money" size={48} color={theme.colors.text.secondary} />
            <Text style={styles.emptyText}>No reimbursement requests yet</Text>
            <Text style={styles.emptySubtext}>
              Submit your first expense to see it here
            </Text>
          </View>
        ) : (
          reimbursementHistory.map((reimbursement, index) => (
            <View key={index} style={styles.reimbursementCard}>
              <View style={styles.reimbursementHeader}>
                <View style={styles.reimbursementTypeContainer}>
                  <Text style={styles.reimbursementType}>
                    {ReimbursementService.getReimbursementTypeDisplayName(reimbursement.reimbursementType)}
                  </Text>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(reimbursement.status) }]}>
                    <Text style={styles.statusText}>
                      {ReimbursementService.getReimbursementStatusDisplayName(reimbursement.status)}
                    </Text>
                  </View>
                </View>
                {reimbursement.status === 'pending' && (
                  <TouchableOpacity
                    style={styles.cancelButton}
                    onPress={() => handleCancelReimbursement(reimbursement.id)}
                  >
                    <FontAwesome name="times" size={16} color={theme.colors.error} />
                  </TouchableOpacity>
                )}
              </View>

              <View style={styles.amountContainer}>
                <Text style={styles.amountValue}>
                  {ReimbursementService.formatCurrency(reimbursement.amount)}
                </Text>
              </View>

              <View style={styles.reimbursementDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Date:</Text>
                  <Text style={styles.detailValue}>
                    {formatDate(reimbursement.date)}
                  </Text>
                </View>

                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Description:</Text>
                  <Text style={styles.detailValue}>{reimbursement.description}</Text>
                </View>

                {reimbursement.category && (
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Category:</Text>
                    <Text style={styles.detailValue}>{reimbursement.category}</Text>
                  </View>
                )}

                {reimbursement.comments && (
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Comments:</Text>
                    <Text style={styles.detailValue}>{reimbursement.comments}</Text>
                  </View>
                )}

                {reimbursement.receipt && (
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Receipt:</Text>
                    <Text style={[styles.detailValue, { color: theme.colors.primary }]}>
                      ✓ Attached
                    </Text>
                  </View>
                )}
              </View>
            </View>
          ))
        )}
      </View>

      {/* Reimbursement Application Modal */}
      <Modal
        visible={showApplicationForm}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <ReimbursementForm
          onSuccess={() => {
            setShowApplicationForm(false);
            loadReimbursementData();
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
  statsContainer: {
    padding: theme.spacing.xl,
  },
  sectionTitle: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.lg,
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
  totalAmountCard: {
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    ...theme.shadows.sm,
  },
  totalAmountLabel: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.inverse,
    opacity: 0.9,
  },
  totalAmountValue: {
    fontSize: theme.typography.h1.fontSize,
    fontWeight: theme.typography.h1.fontWeight,
    color: theme.colors.text.inverse,
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
  reimbursementCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    ...theme.shadows.sm,
  },
  reimbursementHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  reimbursementTypeContainer: {
    flex: 1,
  },
  reimbursementType: {
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
  amountContainer: {
    marginBottom: theme.spacing.md,
  },
  amountValue: {
    fontSize: theme.typography.h2.fontSize,
    fontWeight: theme.typography.h2.fontWeight,
    color: theme.colors.primary,
  },
  reimbursementDetails: {
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