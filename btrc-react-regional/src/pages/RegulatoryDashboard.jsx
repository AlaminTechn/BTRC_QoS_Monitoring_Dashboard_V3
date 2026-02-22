/**
 * Regulatory Dashboard
 * Main container with 3 tabs: R2.1 SLA Monitoring, R2.2 Regional Analysis, R2.3 Violation Reporting
 * Global date range filter shared across all tabs
 */

import React, { useState } from 'react';
import { Tabs, DatePicker, Space, Tag, Button, Tooltip } from 'antd';
import { DatabaseOutlined, EnvironmentOutlined, WarningOutlined, CalendarOutlined, CloseCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import RegionalAnalysis from './RegionalAnalysis';
import SLAMonitoring from './SLAMonitoring';
import ViolationReporting from './ViolationReporting';

const { RangePicker } = DatePicker;

// POC data range: Nov 30 – Dec 15, 2025
const POC_START = dayjs('2025-11-30');
const POC_END   = dayjs('2025-12-15');

const DATE_PRESETS = [
  { label: 'Full Range (POC)', value: [POC_START, POC_END] },
  { label: 'First Week',       value: [POC_START, dayjs('2025-12-06')] },
  { label: 'Second Week',      value: [dayjs('2025-12-07'), POC_END] },
  { label: 'Dec 1–7',          value: [dayjs('2025-12-01'), dayjs('2025-12-07')] },
  { label: 'Dec 8–15',         value: [dayjs('2025-12-08'), POC_END] },
];

const RegulatoryDashboard = () => {
  const [activeTab, setActiveTab] = useState('r2.2');

  // Global date range state — null means "no date filter" (all data)
  const [dateRange, setDateRange] = useState([null, null]);

  // Format dates as YYYY-MM-DD strings for Metabase API (null if not set)
  const startDate = dateRange[0] ? dateRange[0].format('YYYY-MM-DD') : null;
  const endDate   = dateRange[1] ? dateRange[1].format('YYYY-MM-DD') : null;

  const isDateActive = Boolean(startDate && endDate);

  const handleClearDate = () => setDateRange([null, null]);

  const tabItems = [
    {
      key: 'r2.1',
      label: (
        <span>
          <DatabaseOutlined />
          R2.1 SLA Monitoring
        </span>
      ),
      children: <SLAMonitoring startDate={startDate} endDate={endDate} />,
    },
    {
      key: 'r2.2',
      label: (
        <span>
          <EnvironmentOutlined />
          R2.2 Regional Analysis
        </span>
      ),
      children: <RegionalAnalysis startDate={startDate} endDate={endDate} />,
    },
    {
      key: 'r2.3',
      label: (
        <span>
          <WarningOutlined />
          R2.3 Violation Reporting
        </span>
      ),
      children: <ViolationReporting startDate={startDate} endDate={endDate} />,
    },
  ];

  return (
    <div style={{ width: '100%', minHeight: '100%' }}>
      {/* Global Date Filter Bar */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '10px 32px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        flexWrap: 'wrap',
      }}>
        <Space align="center">
          <CalendarOutlined style={{ color: '#3b82f6', fontSize: 16 }} />
          <span style={{ fontWeight: 600, color: '#374151', fontSize: 13 }}>
            Date Range:
          </span>
        </Space>

        <RangePicker
          value={dateRange}
          onChange={(vals) => setDateRange(vals || [null, null])}
          format="MMM DD, YYYY"
          allowClear
          presets={DATE_PRESETS}
          disabledDate={(d) => d && (d.isBefore(POC_START, 'day') || d.isAfter(POC_END, 'day'))}
          placeholder={['Start Date', 'End Date']}
          size="middle"
          style={{ width: 280 }}
        />

        {isDateActive ? (
          <>
            <Tag
              color="blue"
              style={{ fontSize: 12, padding: '2px 8px' }}
              icon={<CalendarOutlined />}
            >
              {startDate} → {endDate}
            </Tag>
            <Tooltip title="Clear date filter">
              <Button
                size="small"
                icon={<CloseCircleOutlined />}
                onClick={handleClearDate}
                type="text"
                style={{ color: '#6b7280' }}
              >
                Clear
              </Button>
            </Tooltip>
          </>
        ) : (
          <Tag color="default" style={{ fontSize: 12 }}>
            Showing all POC data (Nov 30 – Dec 15, 2025)
          </Tag>
        )}
      </div>

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        size="large"
        tabBarStyle={{
          margin: '0',
          padding: '0 32px',
          background: 'white',
          borderBottom: '1px solid #f0f0f0',
        }}
        style={{ width: '100%', background: 'white' }}
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
