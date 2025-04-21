import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PublicHolidays from './PublicHolidays';

// Mock any necessary dependencies or API calls
jest.mock('../../utils/api', () => ({
  getPublicHolidays: jest.fn(() => Promise.resolve([])), // Mock API call
}));

describe('PublicHolidays Component', () => {
  test('renders the component', () => {
    render(<PublicHolidays />);
    expect(screen.getByText(/Public Holidays/i)).toBeInTheDocument(); // Adjust text as needed
  });

  test('displays a list of public holidays', async () => {
    // Mock API response with sample data
    const mockHolidays = [
      { id: 1, name: 'New Year', date: '2024-01-01' },
      { id: 2, name: 'Christmas', date: '2024-12-25' },
    ];
    require('../../utils/api').getPublicHolidays.mockResolvedValue(mockHolidays);

    render(<PublicHolidays />);

    // Wait for the holidays to load (adjust based on your implementation)
    const holidayList = await screen.findAllByRole('listitem'); // Assuming holidays are displayed in a list
    expect(holidayList).toHaveLength(mockHolidays.length);

    // Check if holiday names are displayed (adjust based on your implementation)
    expect(screen.getByText(/New Year/i)).toBeInTheDocument();
    expect(screen.getByText(/Christmas/i)).toBeInTheDocument();
  });

  // Add more tests for adding/deleting holidays if applicable
  // Example (adjust based on your actual implementation):
  // test('handles adding a new holiday', async () => { ... });
  // test('handles deleting a holiday', async () => { ... });
});