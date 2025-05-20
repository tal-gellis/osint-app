import { useState } from 'react';
import type { FormEvent } from 'react';
import type { ScanRequest } from '../types';
import { ScanStatus } from '../types';

interface ScanFormProps {
  currentDomain: string;
  status: ScanStatus;
  onSubmit: (request: ScanRequest) => void;
}

export const ScanForm = ({ currentDomain, status, onSubmit }: ScanFormProps) => {
  const [domain, setDomain] = useState('');
  const [useTheHarvester, setUseTheHarvester] = useState(true);
  const [useAmass, setUseAmass] = useState(true);
  const isLoading = status === ScanStatus.LOADING;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!domain.trim()) return;

    onSubmit({
      domain: domain.trim(),
      options: {
        useTheHarvester,
        useAmass,
      },
    });
  };

  return (
    <div className="scan-form">
      <h2>Start New OSINT Scan</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="domain">Domain Name (e.g., example.com)</label>
          <input
            type="text"
            id="domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="Enter domain name"
            disabled={isLoading}
            pattern="^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
            title="Please enter a valid domain name (e.g., example.com)"
            required
          />
        </div>

        <div className="form-group tools-selection">
          <h3>Tools to use:</h3>
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="theHarvester"
              checked={useTheHarvester}
              onChange={() => setUseTheHarvester(!useTheHarvester)}
              disabled={isLoading}
            />
            <label htmlFor="theHarvester">theHarvester</label>
          </div>
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="amass"
              checked={useAmass}
              onChange={() => setUseAmass(!useAmass)}
              disabled={isLoading}
            />
            <label htmlFor="amass">Amass</label>
          </div>
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={isLoading || !domain.trim() || (!useTheHarvester && !useAmass)}
        >
          {isLoading ? 'Scanning...' : 'Start Scan'}
        </button>
      </form>

      {isLoading && (
        <div className="scan-status">
          <div className="spinner"></div>
          <p>Running scan on <strong>{currentDomain}</strong>...</p>
          <p className="scan-note">Results will appear automatically when tools complete.</p>
        </div>
      )}
    </div>
  );
}; 