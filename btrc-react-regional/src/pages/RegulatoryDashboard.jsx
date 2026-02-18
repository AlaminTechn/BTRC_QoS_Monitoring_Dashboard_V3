/**
 * Regulatory Dashboard
 * Main container with 3 tabs: R2.1 SLA Monitoring, R2.2 Regional Analysis, R2.3 Violation Reporting
 */

import React, { useState } from 'react';
import { Tabs } from 'antd';
import { DatabaseOutlined, EnvironmentOutlined, WarningOutlined } from '@ant-design/icons';
import RegionalAnalysis from './RegionalAnalysis';
import SLAMonitoring from './SLAMonitoring';
import ViolationReporting from './ViolationReporting';

const RegulatoryDashboard = () => {
  const [activeTab, setActiveTab] = useState('r2.2');

  const tabItems = [
    {
      key: 'r2.1',
      label: (
        <span>
          <DatabaseOutlined />
          R2.1 SLA Monitoring
        </span>
      ),
      children: <SLAMonitoring />,
    },
    {
      key: 'r2.2',
      label: (
        <span>
          <EnvironmentOutlined />
          R2.2 Regional Analysis
        </span>
      ),
      children: <RegionalAnalysis />,
    },
    {
      key: 'r2.3',
      label: (
        <span>
          <WarningOutlined />
          R2.3 Violation Reporting
        </span>
      ),
      children: <ViolationReporting />,
    },
  ];

  return (
    <div style={{
      width: '100%',
      minHeight: '100%',
      padding: '0',
      margin: '0'
    }}>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        size="large"
        tabBarStyle={{
          margin: '0',
          padding: '12px 32px',
          background: 'white',
          borderBottom: '1px solid #f0f0f0',
        }}
        style={{
          width: '100%',
          background: 'white'
        }}
        tabPaneStyle={{
          width: '100%',
          display: 'block',
          visibility: 'visible',
          opacity: 1,
        }}
      />
    </div>
  );
};

export default RegulatoryDashboard;
