import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ScanForm from '../components/ScanForm';

// Mock the API service
vi.mock('../services/api', () => ({
  startScan: vi.fn().mockResolvedValue({ scan_id: 'test-123', status: 'started' })
}));

describe('ScanForm Component', () => {
  it('renders the form correctly', () => {
    const onScanStarted = vi.fn();
    render(<ScanForm onScanStarted={onScanStarted} />);
    
    // Check if the domain input field is present
    expect(screen.getByPlaceholderText('Enter domain (e.g., example.com)')).toBeInTheDocument();
    
    // Check if the scan button is present
    expect(screen.getByRole('button', { name: /scan domain/i })).toBeInTheDocument();
  });
  
  it('validates domain input', async () => {
    const onScanStarted = vi.fn();
    render(<ScanForm onScanStarted={onScanStarted} />);
    
    // Get the domain input and scan button
    const domainInput = screen.getByPlaceholderText('Enter domain (e.g., example.com)');
    const scanButton = screen.getByRole('button', { name: /scan domain/i });
    
    // Try submitting with empty domain
    fireEvent.click(scanButton);
    
    // Should show validation error
    expect(screen.getByText(/please enter a domain/i)).toBeInTheDocument();
    
    // Enter an invalid domain
    fireEvent.change(domainInput, { target: { value: 'invalid domain' } });
    fireEvent.click(scanButton);
    
    // Should show validation error for invalid format
    expect(screen.getByText(/invalid domain format/i)).toBeInTheDocument();
    
    // Enter a valid domain
    fireEvent.change(domainInput, { target: { value: 'example.com' } });
    fireEvent.click(scanButton);
    
    // Callback should be called with scan data
    expect(onScanStarted).toHaveBeenCalledWith(expect.objectContaining({
      scan_id: 'test-123',
      status: 'started'
    }));
  });
}); 