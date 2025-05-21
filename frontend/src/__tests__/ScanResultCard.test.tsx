import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ScanResultCard from '../components/ScanResultCard';

// Mock the API service
vi.mock('../services/api', () => ({
  exportScan: vi.fn().mockImplementation(() => {
    // Create a mock download response
    const blob = new Blob(['test data'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    return Promise.resolve(blob);
  })
}));

describe('ScanResultCard Component', () => {
  const mockScan = {
    scan_id: 'test-123',
    domain: 'example.com',
    status: 'completed',
    start_time: '2025-05-20T10:00:00',
    end_time: '2025-05-20T10:01:30',
    results: {
      subdomains: ['sub1.example.com', 'sub2.example.com'],
      emails: ['admin@example.com', 'info@example.com'],
      ips: ['1.1.1.1', '2.2.2.2'],
      social_profiles: ['https://twitter.com/example']
    }
  };
  
  it('renders the scan result card correctly', () => {
    render(<ScanResultCard scan={mockScan} />);
    
    // Check if domain is displayed
    expect(screen.getByText('example.com')).toBeInTheDocument();
    
    // Check if status is displayed
    expect(screen.getByText(/completed/i)).toBeInTheDocument();
    
    // Check if summary counts are displayed
    expect(screen.getByText('2 subdomains')).toBeInTheDocument();
    expect(screen.getByText('2 emails')).toBeInTheDocument();
    expect(screen.getByText('2 IPs')).toBeInTheDocument();
    expect(screen.getByText('1 social profile')).toBeInTheDocument();
    
    // Check if export button is present
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });
  
  it('displays the details when view details is clicked', () => {
    render(<ScanResultCard scan={mockScan} />);
    
    // Initially, details should not be visible
    expect(screen.queryByText('sub1.example.com')).not.toBeInTheDocument();
    
    // Click the view details button
    fireEvent.click(screen.getByRole('button', { name: /view details/i }));
    
    // Now details should be visible
    expect(screen.getByText('sub1.example.com')).toBeInTheDocument();
    expect(screen.getByText('sub2.example.com')).toBeInTheDocument();
    expect(screen.getByText('admin@example.com')).toBeInTheDocument();
    expect(screen.getByText('info@example.com')).toBeInTheDocument();
    expect(screen.getByText('1.1.1.1')).toBeInTheDocument();
    expect(screen.getByText('2.2.2.2')).toBeInTheDocument();
    expect(screen.getByText('https://twitter.com/example')).toBeInTheDocument();
  });
  
  it('handles in-progress scans correctly', () => {
    const inProgressScan = {
      ...mockScan,
      status: 'running',
      end_time: null,
      results: null
    };
    
    render(<ScanResultCard scan={inProgressScan} />);
    
    // Should show running status
    expect(screen.getByText(/running/i)).toBeInTheDocument();
    
    // Export button should be disabled
    expect(screen.getByRole('button', { name: /export/i })).toBeDisabled();
  });
}); 