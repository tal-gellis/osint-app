import type { ScanRequest, ScanResult } from '../types';

// For Docker deployments, use relative path to make proxying work
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'  // Development - direct to backend
  : '';  // Production - use proxy pass through nginx

// Helper to transform backend response format to frontend format
const transformScanData = (data: any): ScanResult => {
  return {
    id: data.scan_id,
    domain: data.domain,
    startTime: data.start_time,
    endTime: data.end_time || '',
    summary: {
      subdomains: data.results?.subdomains?.length || 0,
      emails: data.results?.emails?.length || 0,
      ips: data.results?.ips?.length || 0,
      socialProfiles: data.results?.social_profiles?.length || 0
    },
    details: {
      subdomains: data.results?.subdomains || [],
      emails: data.results?.emails || [],
      ips: data.results?.ips || [],
      socialProfiles: data.results?.social_profiles || []
    }
  };
};

export const api = {
  async startScan(request: ScanRequest): Promise<{ scanId: string }> {
    const response = await fetch(`${API_BASE_URL}/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ domain: request.domain }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start scan');
    }

    const data = await response.json();
    // Convert from backend's scan_id to frontend's scanId
    return { scanId: data.scan_id };
  },

  async getScanStatus(scanId: string): Promise<ScanResult> {
    const response = await fetch(`${API_BASE_URL}/scans/${scanId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get scan status');
    }

    const data = await response.json();
    return transformScanData(data);
  },

  async getAllScans(): Promise<ScanResult[]> {
    const response = await fetch(`${API_BASE_URL}/scans`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get scans');
    }

    const data = await response.json();
    return data.map(transformScanData);
  },

  async exportToExcel(scanId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/export/${scanId}`, {
      headers: {
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to export scan');
    }

    return response.blob();
  }
}; 