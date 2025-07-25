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
import DateTimePicker from '@react-native-community/datetimepicker';
import { FontAwesome } from '@expo/vector-icons';
import { LeaveService, LeaveApplicationData } from '../services/LeaveService';
import { LeaveType } from '@pmssrc/shared-types';
import { useAuth } from '../../../providers/AuthProvider';
import { theme } from '../../../styles/theme';

interface LeaveApplicationFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const LeaveApplicationForm: React.FC<LeaveApplicationFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showStartDatePicker, setShowStartDatePicker] = useState(false);
  const [showEndDatePicker, setShowEndDatePicker] = useState(false);
  
  const [formData, setFormData] = useState<LeaveApplicationData>({
    leaveType: 'casual',
    startDate: '',
    endDate: '',
    reason: '',
    halfDay: false,
    halfDayType: undefined,
  });

  const leaveTypes: { value: LeaveType; label: string }[] = [
    { value: 'casual', label: 'Casual Leave' },
    { value: 'sick', label: 'Sick Leave' },
    { value: 'annual', label: 'Annual Leave' },
    { value: 'maternity', label: 'Maternity Leave' },
    { value: 'paternity', label: 'Paternity Leave' },
    { value: 'bereavement', label: 'Bereavement Leave' },
    { value: 'other', label: 'Other Leave' },
  ];

  const halfDayTypes = [
    { value: 'morning', label: 'Morning' },
    { value: 'afternoon', label: 'Afternoon' },
  ];

  const handleDateChange = (event: any, selectedDate?: Date, isStartDate = true) => {
    if (isStartDate) {
      setShowStartDatePicker(false);
    } else {
      setShowEndDatePicker(false);
    }

    if (selectedDate) {
      const dateString = selectedDate.toISOString().split('T')[0];
      if (isStartDate) {
        setFormData(prev => ({ ...prev, startDate: dateString }));
      } else {
        setFormData(prev => ({ ...prev, endDate: dateString }));
      }
    }
  };

  const handleSubmit = async () => {
    if (!user) return;

    // Validate form
    const validation = LeaveService.validateLeaveApplication(formData);
    if (!validation.isValid) {
      Alert.alert('Validation Error', validation.errors.join('\n'));
      return;
    }

    try {
      setIsLoading(true);
      await LeaveService.applyLeave(user.id, formData);
      Alert.alert('Success', 'Leave application submitted successfully!');
      onSuccess?.();
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to submit leave application');
    } finally {
      setIsLoading(false);
    }
  };

  const duration = formData.startDate && formData.endDate
    ? LeaveService.calculateLeaveDuration(formData.startDate, formData.endDate, formData.halfDay)
    : 0;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Apply for Leave</Text>
        <Text style={styles.subtitle}>Submit your leave application</Text>
      </View>

      <View style={styles.form}>
        {/* Leave Type */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Leave Type *</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={formData.leaveType}
              onValueChange={(value) => setFormData(prev => ({ ...prev, leaveType: value }))}
              style={styles.picker}
            >
              {leaveTypes.map((type) => (
                <Picker.Item key={type.value} label={type.label} value={type.value} />
              ))}
            </Picker>
          </View>
        </View>

        {/* Start Date */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Start Date *</Text>
          <TouchableOpacity
            style={styles.dateInput}
            onPress={() => setShowStartDatePicker(true)}
          >
            <Text style={styles.dateText}>
              {formData.startDate || 'Select start date'}
            </Text>
            <FontAwesome name="calendar" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* End Date */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>End Date *</Text>
          <TouchableOpacity
            style={styles.dateInput}
            onPress={() => setShowEndDatePicker(true)}
          >
            <Text style={styles.dateText}>
              {formData.endDate || 'Select end date'}
            </Text>
            <FontAwesome name="calendar" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Duration Display */}
        {duration > 0 && (
          <View style={styles.durationContainer}>
            <Text style={styles.durationText}>
              Duration: {duration} {duration === 1 ? 'day' : 'days'}
            </Text>
          </View>
        )}

        {/* Half Day Toggle */}
        <View style={styles.formGroup}>
          <View style={styles.switchContainer}>
            <Text style={styles.label}>Half Day</Text>
            <Switch
              value={formData.halfDay}
              onValueChange={(value) => setFormData(prev => ({ 
                ...prev, 
                halfDay: value,
                halfDayType: value ? 'morning' : undefined
              }))}
              trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              thumbColor={formData.halfDay ? theme.colors.primary : theme.colors.disabled}
            />
          </View>
        </View>

        {/* Half Day Type */}
        {formData.halfDay && (
          <View style={styles.formGroup}>
            <Text style={styles.label}>Half Day Type *</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.halfDayType}
                onValueChange={(value) => setFormData(prev => ({ ...prev, halfDayType: value }))}
                style={styles.picker}
              >
                {halfDayTypes.map((type) => (
                  <Picker.Item key={type.value} label={type.label} value={type.value} />
                ))}
              </Picker>
            </View>
          </View>
        )}

        {/* Reason */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Reason *</Text>
          <TextInput
            style={styles.textArea}
            value={formData.reason}
            onChangeText={(text) => setFormData(prev => ({ ...prev, reason: text }))}
            placeholder="Please provide a reason for your leave"
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />
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
            style={[styles.button, styles.submitButton, isLoading && styles.buttonDisabled]}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            <Text style={styles.submitButtonText}>
              {isLoading ? 'Submitting...' : 'Submit Application'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Date Pickers */}
      {showStartDatePicker && (
        <DateTimePicker
          value={formData.startDate ? new Date(formData.startDate) : new Date()}
          mode="date"
          display="default"
          onChange={(event, date) => handleDateChange(event, date, true)}
          minimumDate={new Date()}
        />
      )}

      {showEndDatePicker && (
        <DateTimePicker
          value={formData.endDate ? new Date(formData.endDate) : new Date()}
          mode="date"
          display="default"
          onChange={(event, date) => handleDateChange(event, date, false)}
          minimumDate={formData.startDate ? new Date(formData.startDate) : new Date()}
        />
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
  pickerContainer: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.surface,
  },
  picker: {
    height: 50,
  },
  dateInput: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  dateText: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.primary,
  },
  durationContainer: {
    backgroundColor: theme.colors.info,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.lg,
  },
  durationText: {
    fontSize: theme.typography.body1.fontSize,
    fontWeight: '600',
    color: theme.colors.text.inverse,
    textAlign: 'center',
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  textArea: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.primary,
    minHeight: 100,
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
  submitButton: {
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
  submitButtonText: {
    fontSize: theme.typography.button.fontSize,
    fontWeight: theme.typography.button.fontWeight,
    color: theme.colors.text.inverse,
  },
}); 