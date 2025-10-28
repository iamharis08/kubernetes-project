// In frontend/src/App.js
import React, { useState } from 'react';
import './App.css';
import './index.css'; // Make sure you import global styles

const API_URL = "/api";

function App() {
  const [phiResult, setPhiResult] = useState('Click "Fetch Data" to see the result.');
  const [traceResult, setTraceResult] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [securityTrace, setSecurityTrace] = useState(['Click the button below to prove firewall enforcement.']);
  const [isSecurityLoading, setIsSecurityLoading] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    setPhiResult('Loading...');
    setTraceResult([]);
    try {
      const response = await fetch(`${API_URL}/patient/123`);
      const data = await response.json();
      if (!response.ok || !data.phi_data) {
        const errorMsg = data.trace ? data.trace.join('\n') : (data.detail || 'Unknown error');
        throw new Error(`API Error:\n${errorMsg}`);
      }
      setPhiResult(JSON.stringify(data.phi_data, null, 2));
      setTraceResult(data.trace);
    } catch (error) {
      setPhiResult(error.message);
      setTraceResult([]);
    } finally {
      setIsLoading(false);
    }
  };

  const runSecurityCheck = async () => {
    setIsSecurityLoading(true);
    setSecurityTrace(['Initiating UNAUTHORIZED network test...']);

    try {
      const response = await fetch(`${API_URL}/check`);
      const data = await response.json();

      setSecurityTrace(data.trace);
    } catch (error) {
      setSecurityTrace([`FATAL ERROR: Could not communicate with API Gateway. Check Ingress/Load Balancer.`]);
    } finally {
      setIsSecurityLoading(false);
    }
  };

  // Determine if the security trace indicates a successful block
  const isSecurityBlocked = securityTrace && Array.isArray(securityTrace) && securityTrace.some(s => s.includes('BLOCKED') || s.includes('ERROR') || s.includes('timed out'));

  return (
    <div className="App">
      <header className="App-header">
        <div className="Header-content">🛡️ Haris' Secure PHI Platform</div>
      </header>

      <main className="container">
        <div className="Card">
          <div className="Card-header">
            <h2>GKE Autopilot & Zero-Trust Demo</h2>
            <p>This application demonstrates a HIPAA-compliant architecture using GKE Autopilot, Workload Identity, and native NetworkPolicy firewalls.</p>
          </div>

          {/* --- Compliance Notice Banner --- */}
          <div className="compliance-notice">
            <span role="img" aria-label="warning">⚠️</span>
            <strong>Note:</strong> This project demonstrates key HIPAA security principles but is **in progress**. See the checklist below for remaining compliance steps.
          </div>
          {/* --- End Notice Banner --- */}

          <button onClick={fetchData} disabled={isLoading} className="Card-button">
            {isLoading ? 'Loading...' : 'Run Authorized Flow (Fetch Patient ID: 123)'}
          </button>

          {/* Results Grid - Data Trace and PHI (Stacked Layout) */}
          <div className="content-grid">
            <div className="result-box">
              <h3>PHI Data Result:</h3>
              <pre className="data-pre">{phiResult}</pre>
            </div>
            <div className="result-box">
              <h3>Live Data Flow (Trace):</h3>
              <div className="trace-box">
                <ul>
                  {traceResult.map((step, index) => (
                    <li key={index}>
                      <span>{step.split(']:')[0]}]:</span>{step.split(']:')[1]}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* --- Updated Firewall Proof Section --- */}
          <div className="firewall-proof-section">
            <hr className="section-divider" />
            <h3 className="section-title">Zero-Trust Firewall Proof</h3>

            <div className="description-text">
                <p>This interactive test vividly demonstrates <strong className="highlight">Zero-Trust NetworkPolicy</strong> enforcement in action.</p>
                <p>
                    It instructs the <strong className="highlight">API Gateway</strong> to attempt an <strong className="highlight">unauthorized internal connection</strong> directly to the <strong className="highlight">Audit Service</strong>, deliberately bypassing the <strong className="highlight">PHI Service</strong>.
                </p>
                <p>
                    Watch how the API Gateway's <strong className="highlight">egress (outgoing) NetworkPolicy</strong> immediately <strong className="highlight">blocks</strong> this forbidden communication, resulting in a crucial connection timeout.
                </p>
            </div>

            <button onClick={runSecurityCheck} disabled={isSecurityLoading} className="Card-button secondary firewall-button">
                {isSecurityLoading ? 'Testing Denial...' : 'Run Firewall Denial Test'}
            </button>

            <div className={`trace-box security-trace-display ${isSecurityBlocked ? 'security-active' : ''}`}>
                <ul>
                    {securityTrace && Array.isArray(securityTrace) && securityTrace.map((step, index) => (
                         <li key={index} className={(step.includes('BLOCKED') || step.includes('ERROR') || step.includes('timed out')) ? 'security-blocked' : ''}>
                             {/* Conditionally render for unauthorized trace steps */}
                            {(step.startsWith('1.') || step.startsWith('2.')) && step.includes(']:') ?
                                <><span>{step.split(']:')[0]}]:</span>{step.split(']:')[1]}</> :
                                step // Render success/error message directly
                            }
                        </li>
                    ))}
                </ul>
            </div>
          </div>
          {/* --- End Updated Section --- */}

          {/* --- HIPAA Compliance Checklist Section --- */}
          <div className="compliance-checklist-section">
              <hr className="section-divider" />
              <h3 className="section-title">HIPAA Compliance Checklist</h3>
              <div className="checklist-columns">
                  <div className="checklist-column">
                      <h4>Implemented Features (✅):</h4>
                      <ul className="checklist implemented">
                          <li>Infrastructure: GKE Autopilot (HIPAA Eligible)</li>
                          <li>Network Isolation: Kubernetes NetworkPolicy (Ingress & Egress)</li>
                          <li>Internal Encryption: Anthos Service Mesh (Automatic mTLS)</li>
                          <li>Service Identity: Workload Identity (Secure GCP API Access)</li>
                          <li>Private Cluster: Nodes have no public IPs</li>
                      </ul>
                  </div>
                  <div className="checklist-column">
                      <h4>Next Steps for Full Compliance (⚪):</h4>
                      <ul className="checklist needed">
                          <li>Encryption at Rest (Secrets, DBs via CMEK)</li>
                          <li>External Encryption (HTTPS/TLS on Ingress)</li>
                          <li>Strict Access Control (IAM/RBAC Least Privilege)</li>
                          <li>Audit Logging (GKE Data Access Logs & App Audit Trail)</li>
                          <li>Vulnerability Scanning (Artifact Registry Scanning)</li>
                          <li>Formal BAA with Google Cloud</li>
                          <li>(Advanced) Private Google Access / VPC Service Controls</li>
                      </ul>
                  </div>
              </div>
          </div>
          {/* --- End Section --- */}

          {/* --- Architecture & Explanation Section --- */}
          <div className="architecture-section">
             <hr className="section-divider" />
            <h3 className="section-title">System Architecture & NetworkPolicy</h3>

            <p style={{textAlign: 'left', maxWidth: '800px', margin: '1rem auto'}}>
              This platform uses **Zero-Trust networking** via Kubernetes NetworkPolicies for HIPAA compliance.
            </p>
            <ul className="explanation-list">
              <li>
                <strong>Default Isolation:</strong> Pods start isolated, unable to communicate.
              </li>
              <li>
                <strong>Ingress Control:</strong> Strict rules define allowed incoming connections (e.g., only API Gateway can call PHI Service).
              </li>
              <li>
                <strong>Egress Control:</strong> Strict rules define allowed outgoing connections, blocking unauthorized internet access and enforcing the specific app flow (API Gateway -> PHI -> Audit). This prevents data exfiltration.
              </li>
              <li>
                <strong>mTLS Encryption:</strong> Anthos Service Mesh automatically encrypts all internal pod-to-pod communication.
              </li>
            </ul>
            <p style={{textAlign: 'left', maxWidth: '800px', margin: '1rem auto'}}>
              The custom made diagram made in Mermaid Charts illustrates this secure flow. The "Firewall Denial Test" above demonstrates egress blocking.
            </p>

            <img
              src="/architecture.svg" /* Assuming SVG */
              alt="GKE Zero-Trust Architecture Diagram"
              className="architecture-image"
            />
          </div>
          {/* --- End Section --- */}

        </div>
      </main>
    </div>
  );
}

export default App;