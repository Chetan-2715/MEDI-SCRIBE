import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// ─── Google OAuth Redirect Handler ───────────────────────────────
// When Google redirects back, the URL looks like:
//   http://localhost:3000#id_token=xxx&token_type=Bearer&...
// We intercept this BEFORE React renders.
const hash = window.location.hash;
if (hash && hash.includes('id_token=') && !hash.startsWith('#/')) {
  // This is a Google OAuth callback, NOT a React route
  const params = new URLSearchParams(hash.substring(1));
  const idToken = params.get('id_token');

  if (idToken) {
    // Show a loading state while we process
    document.body.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:system-ui,sans-serif;background:#f8fafc;">
        <div style="text-align:center;background:white;padding:40px;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
          <div style="width:40px;height:40px;border:4px solid #e2e8f0;border-top-color:#0d9488;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px;"></div>
          <h2 style="color:#1e293b;margin:0 0 8px;">Signing you in...</h2>
          <p style="color:#64748b;margin:0;font-size:14px;">Verifying your Google account</p>
        </div>
      </div>
      <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
    `;

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    fetch(`${API_URL}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: idToken }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Login failed' }));
          throw new Error(err.detail || 'Google login failed');
        }
        return res.json();
      })
      .then((data) => {
        // Store auth data (matching AuthContext localStorage keys)
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('auth_user', JSON.stringify(data.user));

        // Redirect to dashboard (clean URL)
        window.location.href = '/#/dashboard';
        window.location.reload();
      })
      .catch((err) => {
        document.body.innerHTML = `
          <div style="display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:system-ui,sans-serif;background:#f8fafc;">
            <div style="text-align:center;background:white;padding:40px;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08);max-width:400px;">
              <h2 style="color:#1e293b;margin:0 0 8px;">Login Failed</h2>
              <p style="color:#dc2626;font-size:14px;">${err.message}</p>
              <a href="/#/login" style="display:inline-block;margin-top:16px;color:#0d9488;font-weight:600;text-decoration:none;">← Back to Login</a>
            </div>
          </div>
        `;
      });
  }
  // Stop execution — don't render React app during OAuth callback
} else {
  // ─── Normal App Render ───────────────────────────────────────
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Could not find root element to mount to');
  }

  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  if (!clientId || clientId === 'your_google_client_id_here') {
    console.error('CRITICAL: VITE_GOOGLE_CLIENT_ID is missing or default in .env!');
  } else {
    console.log('Google Client ID Loaded:', clientId.substring(0, 10) + '...');
  }

  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}