"use client";

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [chatHistory, setChatHistory] = useState([
    { sender: 'Operator (10:42 AM)', text: 'Platform online. How can I assist you with your industrial assets?' }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [toast, setToast] = useState<{message: string, type: string} | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/approvals`)
      .then(res => res.json())
      .then(data => setPendingApprovals(data.pending_approvals))
      .catch(err => console.error("Failed to load approvals", err));
  }, []);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const handleIngest = async () => {
    showToast('Ingesting SOPs and parsing diagrams...', 'warning');
    try {
      const res = await fetch(`${API_BASE}/api/ingest`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast(data.message, 'success');
      } else {
        showToast(data.message, 'error');
      }
    } catch (e) {
      showToast('Failed to reach ingestion API.', 'error');
    }
  };

  const handleSend = async () => {
    if (!inputQuery.trim()) return;
    
    const userMsg = { sender: 'Operator (You)', text: inputQuery };
    setChatHistory(prev => [...prev, userMsg]);
    setInputQuery('');
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.text })
      });
      const data = await res.json();
      
      // Artificial delay for "agentic" feel
      setTimeout(async () => {
        const botMsg = { 
          sender: data.agent_name || 'AI System', 
          text: data.diagnosis,
          confidence: data.confidence,
          criticPassed: data.critic_passed,
          citations: data.citations,
          trace: data.trace
        };
        setChatHistory(prev => [...prev, botMsg]);
        setIsTyping(false);

        if (data.draft_work_order) {
          const approvalsRes = await fetch(`${API_BASE}/api/approvals`);
          const approvalsData = await approvalsRes.json();
          setPendingApprovals(approvalsData.pending_approvals);
        }
      }, 1200);

    } catch (err) {
      setIsTyping(false);
      setChatHistory(prev => [...prev, { sender: 'System Error', text: 'Failed to connect to the backend API.' }]);
    }
  };

  const handleAction = async (wo_id: string, action: 'approve' | 'reject') => {
    try {
      const res = await fetch(`${API_BASE}/api/approvals/${wo_id}/${action}`, { method: 'POST' });
      const data = await res.json();
      setPendingApprovals(prev => prev.filter(wo => wo.id !== wo_id));
      showToast(data.message, action === 'approve' ? 'success' : 'warning');
    } catch (err) {
      showToast("Failed to execute action.", 'error');
    }
  };

  return (
    <main className="container">
      {/* Toast Notification */}
      {toast && (
        <div style={{
          position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 1000,
          background: toast.type === 'error' ? 'var(--accent-critical)' : toast.type === 'warning' ? 'var(--accent-warning)' : 'var(--accent-success)',
          color: toast.type === 'warning' ? '#000' : '#fff',
          padding: '1rem 2rem', borderRadius: 'var(--radius-sm)', fontWeight: 'bold',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)', transition: 'all 0.3s ease'
        }}>
          {toast.message}
        </div>
      )}

      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '0.2rem' }}>Unified Operations Brain</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Industrial Knowledge Intelligence Platform</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="btn-secondary" onClick={handleIngest}>⚙️ Ingest Data</button>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <span className="status-dot status-success animate-pulse"></span>
            Online
          </span>
        </div>
      </header>

      <div className="grid-2">
        {/* Left Column: Expert Knowledge Copilot */}
        <section className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '75vh' }}>
          <h2>Expert Knowledge Copilot</h2>
          
          <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {chatHistory.map((msg: any, idx: number) => (
              <div key={idx} style={{ 
                alignSelf: msg.sender.includes('Operator') ? 'flex-start' : 'flex-end', 
                background: msg.sender.includes('Operator') ? 'rgba(255,255,255,0.05)' : 'rgba(0,240,255,0.1)', 
                border: msg.sender.includes('Operator') ? 'none' : '1px solid var(--glass-border)',
                padding: '1rem', 
                borderRadius: 'var(--radius-md)', 
                maxWidth: '90%' 
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', gap: '1rem' }}>
                  <span style={{ fontSize: '0.9rem', color: msg.sender.includes('Operator') ? 'var(--text-secondary)' : 'var(--accent-cyan)', fontWeight: 'bold' }}>
                    {msg.sender}
                  </span>
                  {msg.confidence && (
                    <span style={{ color: 'var(--accent-success)', fontSize: '0.8rem' }}>
                      {(msg.confidence * 100).toFixed(0)}% Confidence
                    </span>
                  )}
                </div>
                
                <p style={{ marginBottom: '1rem', whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                
                {msg.criticPassed !== undefined && (
                  <div style={{ marginBottom: '1rem' }}>
                    <span style={{ fontSize: '0.75rem', background: msg.criticPassed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)', color: msg.criticPassed ? '#10B981' : '#EF4444', padding: '0.2rem 0.5rem', borderRadius: '4px', border: `1px solid ${msg.criticPassed ? '#10B981' : '#EF4444'}` }}>
                      {msg.criticPassed ? '🛡️ Critic Verified' : '⚠️ Critic Failed'}
                    </span>
                  </div>
                )}

                {msg.citations && msg.citations.length > 0 && (
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                    {msg.citations.map((cit: any, i: number) => (
                      <span key={i} style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                        {cit.type === 'graph' ? '🔗 Graph: ' : '📄 Vector: '}{cit.text}
                      </span>
                    ))}
                  </div>
                )}

                {msg.trace && (
                  <details style={{ fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: 'var(--radius-sm)' }}>
                    <summary style={{ cursor: 'pointer', color: 'var(--text-secondary)', userSelect: 'none' }}>View Agent Trace</summary>
                    <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                      {msg.trace.map((t: any, i: number) => (
                        <div key={i} style={{ display: 'grid', gridTemplateColumns: '120px 1fr 50px', gap: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.2rem' }}>
                          <span style={{ color: 'var(--accent-cyan)' }}>{t.step}</span>
                          <span style={{ color: 'var(--text-muted)' }}>{t.detail}</span>
                          <span style={{ color: 'var(--text-secondary)', textAlign: 'right' }}>{t.time}</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}
            
            {isTyping && (
              <div style={{ alignSelf: 'flex-end', padding: '1rem', color: 'var(--accent-cyan)' }}>
                Agent Swarm is thinking <span className="animate-pulse">...</span>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
            <input 
              type="text" 
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="E.g. Why is P-102 vibrating? or Is V-450 compliant?" 
              style={{ flex: 1, background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: 'white', padding: '0.75rem', borderRadius: 'var(--radius-sm)', outline: 'none' }}
              disabled={isTyping}
            />
            <button className="btn-primary" onClick={handleSend} disabled={isTyping}>Send</button>
          </div>
        </section>

        {/* Right Column: Supervisor Action Dashboard */}
        <section className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '75vh' }}>
          <h2>Supervisor Dashboard</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Human-in-the-loop pending approvals</p>
          
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {pendingApprovals.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>No pending actions.</p>
            ) : (
              pendingApprovals.map(wo => (
                <div key={wo.id} style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '1.5rem', borderRadius: 'var(--radius-md)', position: 'relative' }}>
                  <div style={{ position: 'absolute', top: '1rem', right: '1rem' }}>
                    <span className="status-dot status-warning animate-pulse"></span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--accent-warning)' }}>Pending Review</span>
                  </div>
                  
                  <h3 style={{ fontSize: '1.1rem', color: 'var(--accent-warning)' }}>Draft: SAP {wo.id}</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: '0.5rem', margin: '1rem 0', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Asset:</span><span>{wo.AssetID}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Action:</span><span>{wo.Description}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Priority:</span><span style={{ color: 'var(--accent-critical)' }}>{wo.Priority}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Generated By:</span><span>{wo.GeneratedBy}</span>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
                    <button className="btn-primary" style={{ flex: 1, minWidth: '120px' }} onClick={() => handleAction(wo.id, 'approve')}>Approve & Execute</button>
                    <button className="btn-secondary" style={{ flex: 1, minWidth: '120px', borderColor: 'var(--accent-critical)', color: 'var(--accent-critical)' }} onClick={() => handleAction(wo.id, 'reject')}>Reject (Evolve)</button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
