import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AllLeaves from './AllLeaves';

// Mock any necessary dependencies or data
const mockLeaveRequests = [
  { id: 1, employee: 'John Doe', leaveType: 'Annual', startDate: '2024-07-15', endDate: '2024-07-20', status: 'Approved' },
  { id: 2, employee: 'Jane Smith', leaveType: 'Sick', startDate: '2024-08-01', endDate: '2024-08-03', status: 'Pending' },
];

jest.mock('../../utils/api', () => ({
  getAllLeaveRequests: () => Promise.resolve(mockLeaveRequests),
}));

describe('AllLeaves Component', () => {
  test('renders the component', async () => {
    render(<AllLeaves />);
    expect(screen.getByText(/all leave requests/i)).toBeInTheDocument(); // Replace with a text/heading present in your component
  });

  test('displays a list of all leave requests', async () => {
    render(<AllLeaves />);
    // Wait for the data to load (adjust timeout if needed)
    const leaveRequestElements = await screen.findAllByRole('row'); // Assuming leave requests are displayed in rows
    expect(leaveRequestElements).toHaveLength(mockLeaveRequests.length + 1); // +1 for the table header row
    // You might want to add more specific checks for the content of each row
  });

  // Add more tests for filtering if your component has filtering functionality
  // Example:
  // test('filters leave requests by status', async () => {
  //   render(<AllLeaves />);
  //   // Interact with the filter element (e.g., select an option)
  //   const statusFilter = screen.getByRole('combobox', { name: /status/i }); // Adjust if necessary
  //   fireEvent.change(statusFilter, { target: { value: 'Approved' } });
  //   // Check if only approved leave requests are displayed
  //   const leaveRequestElements = await screen.findAllByRole('row');
  //   const approvedRequests = mockLeaveRequests.filter(req => req.status === 'Approved');
  //   expect(leaveRequestElements).toHaveLength(approvedRequests.length + 1);
  // });
});