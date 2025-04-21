import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import UsersList from './UsersList'; // Assuming the path is correct

// Mock any necessary dependencies, e.g., API calls
const mockUsers = [
  { id: 1, name: 'John Doe', email: 'john.doe@example.com' },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com' },
];

jest.mock('../../utils/axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: mockUsers })),
}));

describe('UsersList Component', () => {
  test('renders the component', async () => {
    render(<UsersList />);
    expect(screen.getByText('Users')).toBeInTheDocument(); // Replace with actual heading or text
    // Add more assertions to check for other elements if needed
  });

  test('displays a list of users', async () => {
    render(<UsersList />);
    // Wait for the data to load (adjust the timeout if necessary)
    const userListItems = await screen.findAllByRole('listitem'); // Or appropriate role for user items
    expect(userListItems).toHaveLength(mockUsers.length);

    // Check if user names are displayed
    mockUsers.forEach((user) => {
      expect(screen.getByText(user.name)).toBeInTheDocument();
    });
  });

  // Add tests for user actions (edit/delete) if applicable
  // Example (assuming you have buttons for edit/delete with specific data-testid):
  // test('handles delete action', async () => {
  //   render(<UsersList />);
  //   const deleteButton = await screen.findByTestId(`delete-user-${mockUsers[0].id}`);
  //   fireEvent.click(deleteButton);
  //   // Add assertions to check if the delete action is triggered (e.g., API call)
  // });
});