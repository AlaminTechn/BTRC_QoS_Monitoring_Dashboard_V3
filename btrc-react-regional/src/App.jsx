/**
 * Main App Component
 * Handles authentication and routing
 */

import React, { useState, useEffect } from 'react';
import { Button, Spin, message } from 'antd';
import { LoginOutlined } from '@ant-design/icons';
import RegulatoryDashboard from './pages/RegulatoryDashboard';
import FixedLayout from './components/layout/FixedLayout';
import { useMetabaseAuth } from './hooks/useMetabaseData';
import './App.css';

function App() {
  const { isAuthenticated, login, logout, loading, error } = useMetabaseAuth();
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  // Auto-login on mount
  useEffect(() => {
    const autoLogin = async () => {
      if (!isAuthenticated && !isLoggingIn) {
        setIsLoggingIn(true);
        try {
          const username = import.meta.env.VITE_METABASE_USERNAME;
          const password = import.meta.env.VITE_METABASE_PASSWORD;

          if (username && password) {
            await login(username, password);
            message.success('Connected to Metabase successfully!');
          }
        } catch (err) {
          message.error('Failed to connect to Metabase. Please check your credentials.');
          console.error('Auto-login failed:', err);
        } finally {
          setIsLoggingIn(false);
        }
      }
    };

    autoLogin();
  }, []);

  const handleLogin = async () => {
    setIsLoggingIn(true);
    try {
      const username = import.meta.env.VITE_METABASE_USERNAME;
      const password = import.meta.env.VITE_METABASE_PASSWORD;
      await login(username, password);
      message.success('Connected to Metabase successfully!');
    } catch (err) {
      message.error('Failed to connect to Metabase');
    } finally {
      setIsLoggingIn(false);
    }
  };

  // Loading screen
  if (loading || isLoggingIn) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <p style={{ marginTop: 16, fontSize: 16 }}>Connecting to Metabase...</p>
      </div>
    );
  }

  // Not authenticated screen
  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-box">
          <h1 style={{ marginBottom: 24, fontSize: 28, fontWeight: 'bold' }}>
            BTRC Regulatory Dashboard
          </h1>
          <p style={{ marginBottom: 32, color: '#666' }}>
            SLA Monitoring | Regional Analysis | Violation Reporting
          </p>
          {error && (
            <div
              style={{
                marginBottom: 24,
                padding: 12,
                background: '#fff2f0',
                border: '1px solid #ffccc7',
                borderRadius: 4,
                color: '#cf1322',
              }}
            >
              <strong>Connection Error:</strong> {error.message}
            </div>
          )}
          <Button
            type="primary"
            size="large"
            icon={<LoginOutlined />}
            onClick={handleLogin}
            loading={isLoggingIn}
          >
            Connect to Metabase
          </Button>
          <p style={{ marginTop: 16, fontSize: 12, color: '#999' }}>
            Metabase: {import.meta.env.VITE_METABASE_URL || 'http://localhost:3000'}
          </p>
        </div>
      </div>
    );
  }

  // Main dashboard with sidebar layout
  return (
    <FixedLayout>
      <RegulatoryDashboard />
    </FixedLayout>
  );
}

export default App;
