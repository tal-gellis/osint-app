import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ScanResultCard } from '../components/ScanResultCard';
import { ScanStatus } from '../types';

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
    id: 'test-123',
    domain: 'example.com',
    status: ScanStatus.COMPLETED,
    startTime: '2025-05-20T10:00:00',
    endTime: '2025-05-20T10:01:30',
    summary: {
      subdomains: 2,
      emails: 2,
      ips: 2,
      socialProfiles: 1
    },
    details: {
      subdomains: ['sub1.example.com', 'sub2.example.com'],
      emails: ['admin@example.com', 'info@example.com'],
      ips: ['1.1.1.1', '2.2.2.2'],
      socialProfiles: ['https://twitter.com/example']
    }
  };
  
  it('renders the scan result card correctly', () => {
    render(<ScanResultCard result={mockScan} onExport={() => {}} />);
    
    // Check if domain is displayed
    expect(screen.getByText('example.com')).toBeInTheDocument();
    
    // Check if summary counts are displayed
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Subdomains')).toBeInTheDocument();
    expect(screen.getByText('Emails')).toBeInTheDocument();
    expect(screen.getByText('IP Addresses')).toBeInTheDocument();
    expect(screen.getByText('Social Profiles')).toBeInTheDocument();
    
    // Check if export button is present
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });
  
  it('displays the details when view details is clicked', () => {
    render(<ScanResultCard result={mockScan} onExport={() => {}} />);
    
    // Initially, details should not be visible
    expect(screen.queryByText('Subdomains (2)')).not.toBeInTheDocument();
    
    // Click the view details button
    fireEvent.click(screen.getByRole('button', { name: /view details/i }));
    
    // Now details should be visible
    expect(screen.getByText('Subdomains (2)')).toBeInTheDocument();
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
      status: ScanStatus.LOADING,
      endTime: '', // Empty string instead of null to match type
      summary: {
        subdomains: 0,
        emails: 0,
        ips: 0,
        socialProfiles: 0
      },
      details: {
        subdomains: [],
        emails: [],
        ips: [],
        socialProfiles: []
      }
    };
    
    render(<ScanResultCard result={inProgressScan} onExport={() => {}} />);
    
    // Should show the domain is scanning
    expect(screen.getByText('example.com')).toBeInTheDocument();
  });
}); 