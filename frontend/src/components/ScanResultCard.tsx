import { useState } from 'react';
import type { ScanResult } from '../types';

interface ScanResultCardProps {
  result: ScanResult;
  onExport: (scanId: string) => void;
}

export const ScanResultCard = ({ result, onExport }: ScanResultCardProps) => {
  const [showDetails, setShowDetails] = useState(false);
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getDuration = () => {
    const start = new Date(result.startTime).getTime();
    const end = new Date(result.endTime).getTime();
    const durationMs = end - start;
    const seconds = Math.floor(durationMs / 1000);
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${seconds % 60}s`;
  };

  return (
    <div className="scan-result-card">
      <div className="card-header">
        <h3>{result.domain}</h3>
        <div className="card-actions">
          <button
            className="export-button"
            onClick={() => onExport(result.id)}
            title="Export to Excel"
          >
            Export
          </button>
        </div>
      </div>
      
      <div className="card-meta">
        <span>Start: {formatDate(result.startTime)}</span>
        <span>Duration: {getDuration()}</span>
      </div>
      
      <div className="card-summary">
        <div className="summary-item">
          <span className="summary-count">{result.summary.subdomains}</span>
          <span className="summary-label">Subdomains</span>
        </div>
        <div className="summary-item">
          <span className="summary-count">{result.summary.emails}</span>
          <span className="summary-label">Emails</span>
        </div>
        <div className="summary-item">
          <span className="summary-count">{result.summary.ips}</span>
          <span className="summary-label">IP Addresses</span>
        </div>
        <div className="summary-item">
          <span className="summary-count">{result.summary.socialProfiles}</span>
          <span className="summary-label">Social Profiles</span>
        </div>
      </div>
      
      <div className="card-footer">
        <button 
          className="details-button" 
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? 'Hide Details' : 'View Details'}
        </button>
      </div>
      
      {showDetails && (
        <div className="card-details">
          {result.details.subdomains.length > 0 && (
            <div className="detail-section">
              <h4>Subdomains ({result.details.subdomains.length})</h4>
              <ul className="detail-list">
                {result.details.subdomains.map((item, index) => (
                  <li key={`subdomain-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {result.details.emails.length > 0 && (
            <div className="detail-section">
              <h4>Emails ({result.details.emails.length})</h4>
              <ul className="detail-list">
                {result.details.emails.map((item, index) => (
                  <li key={`email-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {result.details.ips.length > 0 && (
            <div className="detail-section">
              <h4>IP Addresses ({result.details.ips.length})</h4>
              <ul className="detail-list">
                {result.details.ips.map((item, index) => (
                  <li key={`ip-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {result.details.socialProfiles.length > 0 && (
            <div className="detail-section">
              <h4>Social Profiles ({result.details.socialProfiles.length})</h4>
              <ul className="detail-list">
                {result.details.socialProfiles.map((item, index) => (
                  <li key={`social-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 