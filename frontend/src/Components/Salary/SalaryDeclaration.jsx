import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert
} from '@mui/material';
import axios from '../../utils/axios';
import PageLayout from '../../layout/PageLayout';

function SalaryDeclaration() {
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeclarationModal, setShowDeclarationModal] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [declaredValue, setDeclaredValue] = useState('');
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    try {
      const response = await axios.get('/salary-components/declarations/self');
      setComponents(response.data);
    } catch (err) {
      setError(err.message || 'An error occurred while fetching components.');
      setAlert({
        open: true,
        message: err.response?.data?.detail || 'Failed to fetch components',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeclareValue = (component) => {
    setSelectedComponent(component);
    setDeclaredValue(component.declared_value || '');
    setShowDeclarationModal(true);
  };

  const handleCloseModal = () => {
    setShowDeclarationModal(false);
    setSelectedComponent(null);
    setDeclaredValue('');
  };

  const handleSaveDeclaration = async () => {
    try {
      if (!selectedComponent) return;

      const value = parseFloat(declaredValue);
      if (isNaN(value) || value < selectedComponent.min_value || value > selectedComponent.max_value) {
        setAlert({
          open: true,
          message: `Value must be between ${selectedComponent.min_value} and ${selectedComponent.max_value}`,
          severity: 'error'
        });
        return;
      }

      await axios.post('/salary-components/declarations/self', {
        components: [{
          sc_id: selectedComponent.sc_id,
          declared_value: value
        }]
      });

      setAlert({
        open: true,
        message: 'Component value declared successfully',
        severity: 'success'
      });

      handleCloseModal();
      fetchComponents();
    } catch (err) {
      setAlert({
        open: true,
        message: err.response?.data?.detail || 'Failed to declare component value',
        severity: 'error'
      });
    }
  };

  const handleCloseAlert = () => {
    setAlert({ ...alert, open: false });
  };

  return (
    <PageLayout title="Salary Declaration">
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Salary Components Declaration
        </Typography>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Component Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Min Value</TableCell>
                <TableCell>Max Value</TableCell>
                <TableCell>Declared Value</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">Loading...</TableCell>
                </TableRow>
              ) : components.length > 0 ? (
                components.map((component) => (
                  <TableRow key={component.sc_id}>
                    <TableCell>{component.name}</TableCell>
                    <TableCell>{component.type}</TableCell>
                    <TableCell>{component.min_value}</TableCell>
                    <TableCell>{component.max_value}</TableCell>
                    <TableCell>{component.declared_value || '-'}</TableCell>
                    <TableCell>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        onClick={() => handleDeclareValue(component)}
                      >
                        {component.declared_value ? 'Update' : 'Declare'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">No components assigned</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Declaration Modal */}
        <Dialog 
          open={showDeclarationModal} 
          onClose={handleCloseModal}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            {selectedComponent ? `Declare Value for ${selectedComponent.name}` : 'Declare Component Value'}
          </DialogTitle>
          <DialogContent>
            {selectedComponent && (
              <Box sx={{ mt: 2 }}>
                <TextField
                  label="Declared Value"
                  type="number"
                  fullWidth
                  value={declaredValue}
                  onChange={(e) => setDeclaredValue(e.target.value)}
                  inputProps={{
                    min: selectedComponent.min_value,
                    max: selectedComponent.max_value
                  }}
                  helperText={`Must be between ${selectedComponent.min_value} and ${selectedComponent.max_value}`}
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseModal}>Cancel</Button>
            <Button 
              onClick={handleSaveDeclaration} 
              variant="contained" 
              color="primary"
              disabled={!declaredValue}
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>

        <Snackbar 
          open={alert.open} 
          autoHideDuration={6000} 
          onClose={handleCloseAlert}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseAlert} 
            severity={alert.severity}
            sx={{ width: '100%' }}
          >
            {alert.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
}

export default SalaryDeclaration; 