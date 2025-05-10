import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Divider,
  Tooltip,
  Paper
} from '@mui/material';
import { perquisiteSections } from '../utils/taxationConstants';
import AccommodationSection from './perquisites/AccommodationSection';
import CarTransportSection from './perquisites/CarTransportSection';
import MedicalReimbursementSection from './perquisites/MedicalReimbursementSection';
import LeaveTravelAllowanceSection from './perquisites/LeaveTravelAllowanceSection';
import FreeEducationSection from './perquisites/FreeEducationSection';
import GasElectricityWaterSection from './perquisites/GasElectricityWaterSection';
import LoanSection from './perquisites/LoanSection';
import ESOPStockOptionsSection from './perquisites/ESOPStockOptionsSection';
import MovableAssetsSection from './perquisites/MovableAssetsSection';
import OtherPerquisitesSection from './perquisites/OtherPerquisitesSection';

/**
 * TabPanel component for tab content
 * @param {Object} props - Component props
 * @returns {JSX.Element} Tab panel
 */
const TabPanel = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`perquisite-tabpanel-${index}`}
      aria-labelledby={`perquisite-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ px: 3, py: 3, justifyContent: 'center'}}>
          {children}
        </Box>
      )}
    </div>
  );
};

/**
 * Get props for tab
 * @param {number} index - Tab index
 * @returns {Object} Tab props
 */
const a11yProps = (index) => {
  return {
    id: `perquisite-tab-${index}`,
    'aria-controls': `perquisite-tabpanel-${index}`,
  };
};

/**
 * Perquisites Section Component
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Perquisites section component
 */
const PerquisitesSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Perquisites
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Perquisites are taxable benefits provided by an employer to an employee in addition to salary and wages.
        Fill in details for all applicable perquisites.
      </Typography>

      <Paper sx={{ mt: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            aria-label="perquisites tabs"
          >
            {perquisiteSections.map((section, index) => (
              <Tab key={section} label={section} {...a11yProps(index)} />
            ))}
          </Tabs>
        </Box>

        {/* Accommodation Section */}
        <TabPanel value={activeTab} index={0}>
          <AccommodationSection 
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Car & Transport Section */}
        <TabPanel value={activeTab} index={1}>
          <CarTransportSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Medical Reimbursement Section */}
        <TabPanel value={activeTab} index={2}>
          <MedicalReimbursementSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Leave Travel Allowance Section */}
        <TabPanel value={activeTab} index={3}>
          <LeaveTravelAllowanceSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Free Education Section */}
        <TabPanel value={activeTab} index={4}>
          <FreeEducationSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Gas, Electricity, Water Section */}
        <TabPanel value={activeTab} index={5}>
          <GasElectricityWaterSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Interest-free/Concession Loan Section */}
        <TabPanel value={activeTab} index={6}>
          <LoanSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* ESOP & Stock Options Section */}
        <TabPanel value={activeTab} index={7}>
          <ESOPStockOptionsSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Movable Assets Section */}
        <TabPanel value={activeTab} index={8}>
          <MovableAssetsSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>

        {/* Other Perquisites Section */}
        <TabPanel value={activeTab} index={9}>
          <OtherPerquisitesSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default PerquisitesSection; 