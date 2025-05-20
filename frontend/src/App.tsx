import { useState } from 'react'
import './App.css'
import { ScanForm } from './components/ScanForm'
import { ScanResultCard } from './components/ScanResultCard'
import { useScan } from './hooks/useScan'
import type { ScanStatus } from './types'

function App() {
  const [activeTab, setActiveTab] = useState<'scan' | 'results'>('scan')
  const { status, currentDomain, results, error, startScan, exportScan } = useScan()

  const handleTabClick = (tab: 'scan' | 'results') => {
    setActiveTab(tab)
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>OSINT Scanner</h1>
        <nav className="app-nav">
          <button 
            className={`nav-button ${activeTab === 'scan' ? 'active' : ''}`}
            onClick={() => handleTabClick('scan')}
          >
            New Scan
          </button>
          <button 
            className={`nav-button ${activeTab === 'results' ? 'active' : ''}`}
            onClick={() => handleTabClick('results')}
          >
            Results ({results.length})
          </button>
        </nav>
      </header>

      <main className="app-content">
        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => handleTabClick('scan')}>Try Again</button>
          </div>
        )}

        {activeTab === 'scan' && (
          <div className="scan-container">
            <ScanForm 
              currentDomain={currentDomain}
              status={status as ScanStatus}
              onSubmit={startScan}
            />
          </div>
        )}

        {activeTab === 'results' && (
          <div className="results-container">
            <h2>Scan Results</h2>
            {results.length === 0 ? (
              <div className="no-results">
                <p>No scan results yet. Run your first scan to see results here.</p>
                <button 
                  className="new-scan-button"
                  onClick={() => handleTabClick('scan')}
                >
                  Start a Scan
                </button>
              </div>
            ) : (
              <div className="results-list">
                {results.map((result) => (
                  <ScanResultCard
                    key={result.id}
                    result={result}
                    onExport={exportScan}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>OSINT Scanner &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  )
}

export default App
