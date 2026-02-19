/**
 * Violation Reporting Tab (R2.3)
 * Placeholder - Will be implemented with Cards 88-93
 */

import React from 'react';
import { Row, Col, Card, Alert } from 'antd';
import { WarningOutlined } from '@ant-design/icons';

const ViolationReporting = () => {
  return (
    <div style={{ width: '100%', padding: '32px', background: '#f0f2f5', minHeight: '70vh' }}>
      <Card
        bordered={false}
        style={{ marginBottom: 24 }}
        bodyStyle={{ padding: '24px 32px' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <WarningOutlined style={{ fontSize: 32, color: '#ef4444' }} />
          <div>
            <h1 style={{
              fontSize: 28,
              fontWeight: 'bold',
              margin: 0,
              color: '#1f2937'
            }}>
              Violation Reporting
            </h1>
            <p style={{
              fontSize: 14,
              color: '#6b7280',
              margin: 0
            }}>
              Detailed SLA violation analysis and reporting
            </p>
          </div>
        </div>
      </Card>

      <Alert
        title="Coming Soon"
        description="This tab will display recent violations, violation trends by severity, top violating ISPs, violation patterns by time of day, resolution time metrics, and violation heatmaps. Implementation includes Cards 88-93 from Metabase."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[16, 16]}>
        <Col xs={24}>
          <Card title="Recent Violations" bordered={false}>
            <p style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
              Card 88: Recent violations table with time, ISP, location, severity
            </p>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Violation Trend by Severity" bordered={false}>
            <p style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
              Card 89: Multi-series line chart (Critical, High, Medium, Low)
            </p>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Top Violating ISPs" bordered={false}>
            <p style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
              Card 90: Bar chart of ISP violations
            </p>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Violation by Time of Day" bordered={false}>
            <p style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
              Card 91: Bar chart by hour
            </p>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Violation Resolution Time" bordered={false}>
            <p style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
              Card 92: Table showing avg/min/max resolution time
            </p>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Violation Heatmap" bordered={false}>
            <p style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
              Card 93: Heatmap by location and time
            </p>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ViolationReporting;
