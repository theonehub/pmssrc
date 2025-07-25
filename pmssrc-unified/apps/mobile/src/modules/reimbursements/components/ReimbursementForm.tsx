import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Image,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import DateTimePicker from '@react-native-community/datetimepicker';
import * as ImagePicker from 'expo-image-picker';
import { FontAwesome } from '@expo/vector-icons';
import { ReimbursementService, ReimbursementApplicationData } from '../services/ReimbursementService';
import { ReimbursementType } from '@pmssrc/shared-types';
import { useAuth } from '../../../providers/AuthProvider';
import { theme } from '../../../styles/theme';

interface ReimbursementFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ReimbursementForm: React.FC<ReimbursementFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [receiptImage, setReceiptImage] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<ReimbursementApplicationData>({
    reimbursementType: 'travel',
    amount: 0,
    description: '',
    date: '',
    category: '',
  });

  const reimbursementTypes = ReimbursementService.getReimbursementTypes();
  const expenseCategories = ReimbursementService.getExpenseCategories();

  const handleDateChange = (event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (selectedDate) {
      const dateString = selectedDate.toISOString().split('T')[0];
      setFormData(prev => ({ ...prev, date: dateString }));
    }
  };

  const handlePickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        setReceiptImage(base64Image);
        setFormData(prev => ({ ...prev, receipt: base64Image }));
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const handleSubmit = async () => {
    if (!user) return;

    // Validate form
    const validation = ReimbursementService.validateReimbursementApplication(formData);
    if (!validation.isValid) {
      Alert.alert('Validation Error', validation.errors.join('\n'));
      return;
    }

    try {
      setIsLoading(true);
      await ReimbursementService.submitReimbursement(user.id, formData);
      Alert.alert('Success', 'Reimbursement request submitted successfully!');
      onSuccess?.();
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to submit reimbursement request');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Submit Expense</Text>
        <Text style={styles.subtitle}>Request reimbursement for your expenses</Text>
      </View>

      <View style={styles.form}>
        {/* Reimbursement Type */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Expense Type *</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={formData.reimbursementType}
              onValueChange={(value) => setFormData(prev => ({ ...prev, reimbursementType: value }))}
              style={styles.picker}
            >
              {reimbursementTypes.map((type) => (
                <Picker.Item key={type.value} label={type.label} value={type.value} />
              ))}
            </Picker>
          </View>
        </View>

        {/* Amount */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Amount (₹) *</Text>
          <TextInput
            style={styles.input}
            value={formData.amount > 0 ? formData.amount.toString() : ''}
            onChangeText={(text) => {
              const amount = parseFloat(text) || 0;
              setFormData(prev => ({ ...prev, amount }));
            }}
            placeholder="Enter amount"
            keyboardType="numeric"
          />
        </View>

        {/* Date */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Expense Date *</Text>
          <TouchableOpacity
            style={styles.dateInput}
            onPress={() => setShowDatePicker(true)}
          >
            <Text style={styles.dateText}>
              {formData.date || 'Select expense date'}
            </Text>
            <FontAwesome name="calendar" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Category */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Category</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={formData.category}
              onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
              style={styles.picker}
            >
              <Picker.Item label="Select category" value="" />
              {expenseCategories.map((category) => (
                <Picker.Item key={category} label={category} value={category} />
              ))}
            </Picker>
          </View>
        </View>

        {/* Description */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Description *</Text>
          <TextInput
            style={styles.textArea}
            value={formData.description}
            onChangeText={(text) => setFormData(prev => ({ ...prev, description: text }))}
            placeholder="Describe the expense in detail"
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />
        </View>

        {/* Receipt Upload */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Receipt (Optional)</Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={handlePickImage}
          >
            <FontAwesome name="camera" size={20} color={theme.colors.primary} />
            <Text style={styles.uploadButtonText}>
              {receiptImage ? 'Change Receipt' : 'Upload Receipt'}
            </Text>
          </TouchableOpacity>
          
          {receiptImage && (
            <View style={styles.imageContainer}>
              <Image source={{ uri: receiptImage }} style={styles.receiptImage} />
              <TouchableOpacity
                style={styles.removeImageButton}
                onPress={() => {
                  setReceiptImage(null);
                  setFormData(prev => ({ ...prev, receipt: undefined }));
                }}
              >
                <FontAwesome name="times" size={16} color={theme.colors.error} />
              </TouchableOpacity>
            </View>
          )}
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
              {isLoading ? 'Submitting...' : 'Submit Request'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Date Picker */}
      {showDatePicker && (
        <DateTimePicker
          value={formData.date ? new Date(formData.date) : new Date()}
          mode="date"
          display="default"
          onChange={handleDateChange}
          maximumDate={new Date()}
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
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text.primary,
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
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  uploadButtonText: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.primary,
    marginLeft: theme.spacing.sm,
  },
  imageContainer: {
    marginTop: theme.spacing.md,
    position: 'relative',
  },
  receiptImage: {
    width: '100%',
    height: 200,
    borderRadius: theme.borderRadius.md,
  },
  removeImageButton: {
    position: 'absolute',
    top: theme.spacing.sm,
    right: theme.spacing.sm,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.round,
    width: 30,
    height: 30,
    alignItems: 'center',
    justifyContent: 'center',
    ...theme.shadows.sm,
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