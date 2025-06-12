import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, Box, Typography, Tabs, Tab } from '@mui/material';
import { TaxCalculator, TaxDashboard, TaxRecords } from './pages';
import { TaxOptimizationEngine, ScenarioAnalyzer } from './components/analytics';

// Create a simple theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// =============================================================================
// DEMO APP COMPONENT
// =============================================================================

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`demo-tabpanel-${index}`}
      aria-labelledby={`demo-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

export const TaxationV2Demo: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl">
        <Box sx={{ py: 4 }}>
          <Typography variant="h3" gutterBottom textAlign="center">
            🚀 Taxation V2 - Phase 4 Complete
          </Typography>
          <Typography variant="h6" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
            Advanced Analytics & Integration with AI Optimization, Scenario Analysis & API Integrations
          </Typography>
          
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange} centered variant="scrollable">
              <Tab label="📊 Dashboard" />
              <Tab label="🧮 Calculator" />
              <Tab label="📋 Records" />
              <Tab label="🧠 AI Optimization" />
              <Tab label="📈 Scenario Analysis" />
            </Tabs>
          </Box>

          <TabPanel value={activeTab} index={0}>
            <TaxDashboard />
          </TabPanel>
          
          <TabPanel value={activeTab} index={1}>
            <TaxCalculator />
          </TabPanel>
          
          <TabPanel value={activeTab} index={2}>
            <TaxRecords />
          </TabPanel>

          <TabPanel value={activeTab} index={3}>
            <TaxOptimizationEngine 
              onApplyRecommendation={(recommendation) => console.log('Applied optimization:', recommendation)}
              onInvestmentSelect={(investment) => console.log('Selected investment:', investment)}
            />
          </TabPanel>

          <TabPanel value={activeTab} index={4}>
            <ScenarioAnalyzer />
          </TabPanel>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default TaxationV2Demo; 