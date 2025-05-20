export interface ScanResult {
  id: string;
  domain: string;
  startTime: string;
  endTime: string;
  summary: {
    subdomains: number;
    emails: number;
    ips: number;
    socialProfiles: number;
  };
  details: {
    subdomains: string[];
    emails: string[];
    ips: string[];
    socialProfiles: string[];
  };
}

export interface ScanRequest {
  domain: string;
  options?: {
    useTheHarvester: boolean;
    useAmass: boolean;
  };
}

export enum ScanStatus {
  IDLE = 'idle',
  LOADING = 'loading',
  COMPLETED = 'completed',
  ERROR = 'error',
}

export interface ScanState {
  status: ScanStatus;
  currentDomain: string;
  results: ScanResult[];
  error: string | null;
} 