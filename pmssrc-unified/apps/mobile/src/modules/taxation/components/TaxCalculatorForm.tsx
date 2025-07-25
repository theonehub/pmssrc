import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Switch,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { FontAwesome } from '@expo/vector-icons';
import { TaxationService, TaxCalculationData, TaxRegimeComparison } from '../services/TaxationService';
import { TaxRegime } from '@pmssrc/shared-types';
import { theme } from '../../../styles/theme';

interface TaxCalculatorFormProps {
  onCalculationComplete?: (comparison: TaxRegimeComparison) => void;
  onCancel?: () => void;
}

export const TaxCalculatorForm: React.FC<TaxCalculatorFormProps> = ({
  onCalculationComplete,
  onCancel,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  
  const [formData, setFormData] = useState<TaxCalculationData>({
    basicSalary: 0,
    allowances: 0,
    deductions: 0,
    regime: 'old',
    financialYear: TaxationService.getFinancialYears()[0],
    additionalIncome: 0,
    investments: 0,
  });

  const financialYears = TaxationService.getFinancialYears();
  const standardDeductions = TaxationService.getStandardDeductions();

  const handleCalculate = async () => {
    // Validate form
    const validation = TaxationService.validateTaxData(formData);
    if (!validation.isValid) {
      Alert.alert('Validation Error', validation.errors.join('\n'));
      return;
    }

    try {
      setIsLoading(true);
      const comparison = await TaxationService.compareTaxRegimes(formData);
      setShowComparison(true);
      onCalculationComplete?.(comparison);
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to calculate tax');
    } finally {
      setIsLoading(false);
    }
  };

  const renderComparison = (comparison: TaxRegimeComparison) => (
    <View style={styles.comparisonContainer}>
      <Text style={styles.comparisonTitle}>Tax Regime Comparison</Text>
      
      {/* Recommendation */}
      <View style={styles.recommendationCard}>
        <FontAwesome 
          name="lightbulb-o" 
          size={24} 
          color={theme.colors.warning} 
        />
        <Text style={styles.recommendationText}>
          Recommended: {TaxationService.getRegimeDisplayName(comparison.recommendedRegime)}
        </Text>
        <Text style={styles.savingsText}>
          Potential Savings: {TaxationService.formatCurrency(comparison.savings)}
        </Text>
      </View>

      {/* Old Regime */}
      <View style={styles.regimeCard}>
        <Text style={styles.regimeTitle}>Old Regime</Text>
        <View style={styles.breakdownGrid}>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Gross Salary</Text>
            <Text style={styles.breakdownValue}>
              {TaxationService.formatCurrency(comparison.oldRegime.grossSalary)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Deductions</Text>
            <Text style={styles.breakdownValue}>
              {TaxationService.formatCurrency(comparison.oldRegime.totalDeductions)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Taxable Income</Text>
            <Text style={styles.breakdownValue}>
              {TaxationService.formatCurrency(comparison.oldRegime.taxableIncome)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Tax Amount</Text>
            <Text style={[styles.breakdownValue, { color: theme.colors.error }]}>
              {TaxationService.formatCurrency(comparison.oldRegime.taxAmount)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Take Home</Text>
            <Text style={[styles.breakdownValue, { color: theme.colors.success }]}>
              {TaxationService.formatCurrency(comparison.oldRegime.takeHomeSalary)}
            </Text>
          </View>
        </View>
      </View>

      {/* New Regime */}
      <View style={styles.regimeCard}>
        <Text style={styles.regimeTitle}>New Regime</Text>
        <View style={styles.breakdownGrid}>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Gross Salary</Text>
            <Text style={styles.breakdownValue}>
              {TaxationService.formatCurrency(comparison.newRegime.grossSalary)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Deductions</Text>
            <Text style={styles.breakdownValue}>
              {TaxationService.formatCurrency(comparison.newRegime.totalDeductions)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Taxable Income</Text>
            <Text style={styles.breakdownValue}>
              {TaxationService.formatCurrency(comparison.newRegime.taxableIncome)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Tax Amount</Text>
            <Text style={[styles.breakdownValue, { color: theme.colors.error }]}>
              {TaxationService.formatCurrency(comparison.newRegime.taxAmount)}
            </Text>
          </View>
          <View style={styles.breakdownItem}>
            <Text style={styles.breakdownLabel}>Take Home</Text>
            <Text style={[styles.breakdownValue, { color: theme.colors.success }]}>
              {TaxationService.formatCurrency(comparison.newRegime.takeHomeSalary)}
            </Text>
          </View>
        </View>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tax Calculator</Text>
        <Text style={styles.subtitle}>Calculate and compare tax regimes</Text>
      </View>

      {!showComparison ? (
        <View style={styles.form}>
          {/* Basic Salary */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>Basic Salary (₹) *</Text>
            <TextInput
              style={styles.input}
              value={formData.basicSalary > 0 ? formData.basicSalary.toString() : ''}
              onChangeText={(text) => {
                const value = parseFloat(text) || 0;
                setFormData(prev => ({ ...prev, basicSalary: value }));
              }}
              placeholder="Enter basic salary"
              keyboardType="numeric"
            />
          </View>

          {/* Allowances */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>Allowances (₹)</Text>
            <TextInput
              style={styles.input}
              value={formData.allowances > 0 ? formData.allowances.toString() : ''}
              onChangeText={(text) => {
                const value = parseFloat(text) || 0;
                setFormData(prev => ({ ...prev, allowances: value }));
              }}
              placeholder="Enter allowances"
              keyboardType="numeric"
            />
          </View>

          {/* Deductions */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>Deductions (₹)</Text>
            <TextInput
              style={styles.input}
              value={formData.deductions > 0 ? formData.deductions.toString() : ''}
              onChangeText={(text) => {
                const value = parseFloat(text) || 0;
                setFormData(prev => ({ ...prev, deductions: value }));
              }}
              placeholder="Enter deductions"
              keyboardType="numeric"
            />
          </View>

          {/* Financial Year */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>Financial Year</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.financialYear}
                onValueChange={(value) => setFormData(prev => ({ ...prev, financialYear: value }))}
                style={styles.picker}
              >
                {financialYears.map((year) => (
                  <Picker.Item key={year} label={year} value={year} />
                ))}
              </Picker>
            </View>
          </View>

          {/* Additional Income */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>Additional Income (₹)</Text>
            <TextInput
              style={styles.input}
              value={formData.additionalIncome && formData.additionalIncome > 0 ? formData.additionalIncome.toString() : ''}
              onChangeText={(text) => {
                const value = parseFloat(text) || 0;
                setFormData(prev => ({ ...prev, additionalIncome: value }));
              }}
              placeholder="Enter additional income"
              keyboardType="numeric"
            />
          </View>

          {/* Investments */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>Investments (₹)</Text>
            <TextInput
              style={styles.input}
              value={formData.investments && formData.investments > 0 ? formData.investments.toString() : ''}
              onChangeText={(text) => {
                const value = parseFloat(text) || 0;
                setFormData(prev => ({ ...prev, investments: value }));
              }}
              placeholder="Enter investments"
              keyboardType="numeric"
            />
          </View>

          {/* Standard Deductions Info */}
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>Standard Deductions (Old Regime)</Text>
            {standardDeductions.map((deduction, index) => (
              <View key={index} style={styles.deductionItem}>
                <Text style={styles.deductionCategory}>{deduction.category}</Text>
                <Text style={styles.deductionDescription}>{deduction.description}</Text>
                {deduction.maxAmount > 0 && (
                  <Text style={styles.deductionAmount}>
                    Max: {TaxationService.formatCurrency(deduction.maxAmount)}
                  </Text>
                )}
              </View>
            ))}
          </View>

          {/* Action Buttons */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onCancel}
              disabled={isLoading}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.calculateButton, isLoading && styles.buttonDisabled]}
              onPress={handleCalculate}
              disabled={isLoading}
            >
              <Text style={styles.calculateButtonText}>
                {isLoading ? 'Calculating...' : 'Calculate Tax'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.resultContainer}>
          {renderComparison({} as TaxRegimeComparison)}
          <TouchableOpacity
            style={styles.newCalculationButton}
            onPress={() => setShowComparison(false)}
          >
            <Text style={styles.newCalculationButtonText}>New Calculation</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

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
  form: {
    padding: theme.spacing.xl,
  },
  formGroup: {
    marginBottom: theme.spacing.lg,
  },
  label: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.primary,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.surface,
  },
  picker: {
    height: 50,
  },
  infoCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    ...theme.shadows.sm,
  },
  infoTitle: {
    fontSize: theme.typography.h4.fontSize,
    fontWeight: theme.typography.h4.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
  },
  deductionItem: {
    marginBottom: theme.spacing.md,
    paddingBottom: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.divider,
  },
  deductionCategory: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  deductionDescription: {
    fontSize: theme.typography.body2.fontSize,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.xs,
  },
  deductionAmount: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.xs,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.xl,
  },
  button: {
    flex: 1,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    marginHorizontal: theme.spacing.xs,
  },
  cancelButton: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  calculateButton: {
    backgroundColor: theme.colors.primary,
  },
  buttonDisabled: {
    backgroundColor: theme.colors.disabled,
  },
  cancelButtonText: {
    fontSize: theme.typography.button.fontSize,
    fontWeight: theme.typography.button.fontWeight,
    color: theme.colors.text.primary,
  },
  calculateButtonText: {
    fontSize: theme.typography.button.fontSize,
    fontWeight: theme.typography.button.fontWeight,
    color: theme.colors.text.inverse,
  },
  resultContainer: {
    padding: theme.spacing.xl,
  },
  comparisonContainer: {
    gap: theme.spacing.lg,
  },
  comparisonTitle: {
    fontSize: theme.typography.h2.fontSize,
    fontWeight: theme.typography.h2.fontWeight,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  recommendationCard: {
    backgroundColor: theme.colors.warning,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    ...theme.shadows.sm,
  },
  recommendationText: {
    fontSize: theme.typography.h4.fontSize,
    fontWeight: theme.typography.h4.fontWeight,
    color: theme.colors.text.inverse,
    marginTop: theme.spacing.sm,
  },
  savingsText: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.inverse,
    marginTop: theme.spacing.xs,
  },
  regimeCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    ...theme.shadows.sm,
  },
  regimeTitle: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
  },
  breakdownGrid: {
    gap: theme.spacing.sm,
  },
  breakdownItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  breakdownLabel: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.secondary,
  },
  breakdownValue: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    color: theme.colors.text.primary,
  },
  newCalculationButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginTop: theme.spacing.xl,
    ...theme.shadows.sm,
  },
  newCalculationButtonText: {
    fontSize: theme.typography.button.fontSize,
    fontWeight: theme.typography.button.fontWeight,
    color: theme.colors.text.inverse,
  },
}); 