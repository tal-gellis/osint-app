import { useState, useCallback, useEffect } from 'react';
import type { ScanRequest, ScanResult, ScanState } from '../types';
import { ScanStatus } from '../types';
import { api } from '../services/api';

export const useScan = () => {
  const [scanState, setScanState] = useState<ScanState>({
    status: ScanStatus.IDLE,
    currentDomain: '',
    results: [],
    error: null,
  });

  // Load saved results from localStorage on init
  useEffect(() => {
    try {
      const savedResults = localStorage.getItem('osint-scan-results');
      if (savedResults) {
        const parsedResults = JSON.parse(savedResults) as ScanResult[];
        setScanState(prev => ({ ...prev, results: parsedResults }));
      }
    } catch (error) {
      console.error('Failed to load saved results:', error);
    }
  }, []);

  // Save results to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('osint-scan-results', JSON.stringify(scanState.results));
    } catch (error) {
      console.error('Failed to save results:', error);
    }
  }, [scanState.results]);

  const startScan = useCallback(async (request: ScanRequest) => {
    try {
      setScanState(prev => ({
        ...prev,
        status: ScanStatus.LOADING,
        currentDomain: request.domain,
        error: null,
      }));

      const { scanId } = await api.startScan(request);
      
      console.log(`Scan started with ID: ${scanId}`);
      
      // Poll for status until completion
      const pollInterval = setInterval(async () => {
        try {
          console.log(`Polling for scan status: ${scanId}`);
          const result = await api.getScanStatus(scanId);
          console.log(`Received scan result:`, result);
          
          if (result.endTime) {
            clearInterval(pollInterval);
            
            setScanState(prev => ({
              ...prev,
              status: ScanStatus.COMPLETED,
              results: [result, ...prev.results],
            }));
          }
        } catch (error) {
          console.error(`Error polling scan status:`, error);
          clearInterval(pollInterval);
          setScanState(prev => ({
            ...prev,
            status: ScanStatus.ERROR,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
          }));
        }
      }, 2000);
      
      // Cleanup interval on component unmount
      return () => clearInterval(pollInterval);
    } catch (error) {
      setScanState(prev => ({
        ...prev,
        status: ScanStatus.ERROR,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      }));
    }
  }, []);

  const exportScan = useCallback(async (scanId: string) => {
    try {
      const blob = await api.exportToExcel(scanId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `osint-scan-${scanId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export scan:', error);
      alert(error instanceof Error ? error.message : 'Failed to export scan');
    }
  }, []);

  return {
    ...scanState,
    startScan,
    exportScan,
  };
}; 