import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Login from '../../src/Components/Auth/Login'; // Adjust the path as needed
import { BrowserRouter } from 'react-router-dom';

// Mock the useAuth hook
const mockLogin = jest.fn();
jest.mock('../../src/hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
  }),
}));

describe('Login Component', () => {
  beforeEach(() => {
    mockLogin.mockReset();
  });

  it('renders the component', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    expect(screen.getByText(/login/i)).toBeInTheDocument(); // Adjust based on your actual text
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('handles user input changes in the email and password fields', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  it('submits the form with valid credentials', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // You would typically await here for an asynchronous action (like an API call)
    // Since we're mocking useAuth, we can check if it was called correctly
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');

    // Add further assertions based on successful login behavior
    // For example, check if the user is redirected, or if a success message appears
  });

  it('displays error messages for invalid credentials', async () => {
    mockLogin.mockImplementation(() => {
      throw new Error('Invalid credentials');
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    //  Since your login might have an async operation, use findByText
    const errorMessage = await screen.findByText(/invalid credentials/i); // Adjust the error message text as needed
    expect(errorMessage).toBeInTheDocument();
  });
});