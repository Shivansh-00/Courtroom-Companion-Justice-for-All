const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return response.json();
}

export async function uploadDocument(token: string, file: File) {
  const form = new FormData();
  form.append('file', file);
  form.append('language', 'en');
  form.append('jurisdiction', 'global');
  form.append('privacyMode', 'false');

  const response = await fetch(`${API_BASE}/v1/documents`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return response.json();
}

export async function fetchResult(token: string, documentId: string) {
  const response = await fetch(`${API_BASE}/v1/documents/${documentId}/result`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.json();
}
