import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import { ScanForm } from '../components/ScanForm';
import { ScanStatus } from '../types';

// Mock the API service
vi.mock('../services/api', () => ({
  startScan: vi.fn().mockResolvedValue({ scan_id: 'test-123', status: 'started' })
}));

// Basic test for ScanForm component
describe('ScanForm Component', () => {
  test('should render a form with an input and button', () => {
    render(<ScanForm currentDomain="" status={ScanStatus.IDLE} onSubmit={() => {}} />);
    
    // Check if the input exists
    const domainInput = screen.getByPlaceholderText(/enter domain name/i);
    expect(domainInput).toBeInTheDocument();
    
    // Check if the scan button exists
    const scanButton = screen.getByRole('button', { name: /start scan/i });
    expect(scanButton).toBeInTheDocument();
  });
  
  test('should validate domain input', () => {
    render(<ScanForm currentDomain="" status={ScanStatus.IDLE} onSubmit={() => {}} />);
    
    // Get form elements
    const domainInput = screen.getByPlaceholderText(/enter domain name/i);
    const scanButton = screen.getByRole('button', { name: /start scan/i });
    
    // Try invalid domain (empty)
    fireEvent.change(domainInput, { target: { value: '' } });
    expect(scanButton).toBeDisabled();
    
    // Try valid domain
    fireEvent.change(domainInput, { target: { value: 'example.com' } });
    expect(scanButton).not.toBeDisabled();
  });
  
  test('should submit when a valid domain is entered', async () => {
    const mockSubmitHandler = vi.fn();
    render(<ScanForm currentDomain="" status={ScanStatus.IDLE} onSubmit={mockSubmitHandler} />);
    
    // Get form elements
    const domainInput = screen.getByPlaceholderText(/enter domain name/i);
    const scanButton = screen.getByRole('button', { name: /start scan/i });
    
    // Enter valid domain and submit
    fireEvent.change(domainInput, { target: { value: 'example.com' } });
    fireEvent.click(scanButton);
    
    // Check if the callback was called with correct data
    expect(mockSubmitHandler).toHaveBeenCalledWith({
      domain: 'example.com',
      options: {
        useTheHarvester: true,
        useAmass: true
      }
    });
  });
}); 