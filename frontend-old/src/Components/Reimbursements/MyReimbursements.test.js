import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MyReimbursements from './MyReimbursements';

// Mock any necessary dependencies, e.g., API calls
jest.mock('../../utils/axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: [] })), // Mock an empty list of reimbursements initially
}));

describe('MyReimbursements Component', () => {
  test('renders the component', () => {
    render(<MyReimbursements />);
    expect(screen.getByText(/My Reimbursements/i)).toBeInTheDocument(); // Replace with a relevant heading or text
  });

  test('displays a list of user\'s reimbursements', async () => {
    // Mock a list of reimbursements to be returned by the API
    const mockReimbursements = [
      { id: 1, description: 'Travel', amount: 100 },
      { id: 2, description: 'Food', amount: 50 },
    ];
    require('../../utils/axios').get.mockResolvedValueOnce({ data: mockReimbursements });

    render(<MyReimbursements />);

    // Wait for the reimbursements to load and check if they are displayed
    expect(await screen.findByText('Travel')).toBeInTheDocument();
    expect(await screen.findByText('Food')).toBeInTheDocument();
    // You might want to check for other details like amount as well, depending on how it's displayed.
  });

  // Add more test cases as needed, e.g., for handling actions:
  // test('handles submitting new reimbursements', () => { ... });
  // test('handles viewing reimbursement details', () => { ... });
});