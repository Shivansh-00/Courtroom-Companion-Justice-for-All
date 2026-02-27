'use client';

import { useEffect, useMemo, useState } from 'react';
import { fetchResult, login, uploadDocument } from '../lib/api';
import { useAppStore } from '../lib/store';

export default function HomePage() {
  const { token, role, pipeline, setAuth, addEvent } = useAppStore();
  const [email, setEmail] = useState('citizen@example.org');
  const [password, setPassword] = useState('StrongPass#123');
  const [file, setFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [status, setStatus] = useState('Idle');

  useEffect(() => {
    if (!token) return;
    const wsUrl = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws') + `?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (evt) => {
      const data = JSON.parse(evt.data);
      if (data.event === 'pipeline.progress') {
        addEvent(data.payload);
      }
    };

    const heartbeat = setInterval(() => ws.readyState === WebSocket.OPEN && ws.send('ping'), 3000);
    return () => {
      clearInterval(heartbeat);
      ws.close();
    };
  }, [token, addEvent]);

  const progress = useMemo(() => pipeline[pipeline.length - 1]?.progress || 0, [pipeline]);

  const handleLogin = async () => {
    const data = await login(email, password);
    setAuth(data.accessToken, data.role);
    setStatus(`Logged in as ${data.role}`);
  };

  const handleUpload = async () => {
    if (!token || !file) return;
    const data = await uploadDocument(token, file);
    setDocumentId(data.documentId);
    setStatus(`Uploaded ${data.documentId}`);
  };

  const handleGetResult = async () => {
    if (!token || !documentId) return;
    const data = await fetchResult(token, documentId);
    setResult(data);
  };

  return (
    <main style={{ maxWidth: 980, margin: '0 auto', padding: 24 }}>
      <h1>AI Courtroom Companion – Justice for All</h1>
      <p>Real-time legal simplification, prediction, blockchain verification, and multilingual support.</p>

      <section style={{ padding: 16, background: '#111827', borderRadius: 8, marginBottom: 16 }}>
        <h2>1) Sign In</h2>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" style={{ marginRight: 8 }} />
        <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" type="password" style={{ marginRight: 8 }} />
        <button onClick={handleLogin}>Login</button>
        <p>Role: {role || 'none'}</p>
      </section>

      <section style={{ padding: 16, background: '#111827', borderRadius: 8, marginBottom: 16 }}>
        <h2>2) Upload Legal Document</h2>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button onClick={handleUpload} style={{ marginLeft: 8 }}>Upload</button>
        <p>Document ID: {documentId || 'N/A'}</p>
      </section>

      <section style={{ padding: 16, background: '#111827', borderRadius: 8, marginBottom: 16 }}>
        <h2>3) Real-Time Pipeline</h2>
        <div style={{ width: '100%', background: '#374151', borderRadius: 10 }}>
          <div style={{ width: `${progress}%`, background: '#10b981', color: '#111827', padding: 4, borderRadius: 10, transition: 'width 500ms' }}>
            {progress}%
          </div>
        </div>
        <ul>
          {pipeline.map((evt, idx) => (
            <li key={`${evt.stage}-${idx}`}>{evt.stage}: {evt.message}</li>
          ))}
        </ul>
      </section>

      <section style={{ padding: 16, background: '#111827', borderRadius: 8 }}>
        <h2>4) AI + Blockchain Output</h2>
        <button onClick={handleGetResult}>Fetch Result</button>
        {result && (
          <pre style={{ whiteSpace: 'pre-wrap', marginTop: 12 }}>{JSON.stringify(result, null, 2)}</pre>
        )}
      </section>

      <p style={{ marginTop: 16 }}>Status: {status}</p>
    </main>
  );
}
