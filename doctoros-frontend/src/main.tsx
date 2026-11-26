import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import '@fontsource-variable/fraunces';
import '@fontsource-variable/manrope';
import '@fontsource-variable/jetbrains-mono';
import '@fontsource-variable/cinzel';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
        <Toaster position="top-center" toastOptions={{ style: { borderRadius: '12px', fontSize: '14px', background: '#16110D', color: '#F6ECD3' } }} />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
