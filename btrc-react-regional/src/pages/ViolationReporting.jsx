/**
 * Violation Reporting Tab (R2.3)
 * Cards 82-87: KPI scalars, Detail Table, Trend Chart, District Breakdown
 */

import React from 'react';
import { Row, Col, Card, Tag, Spin, Alert } from 'antd';
import { WarningOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import ScalarCard from '../components/charts/ScalarCard';
import DataTable from '../components/charts/DataTable';
import useMetabaseData from '../hooks/useMetabaseData';

// Severity color mapping
const SEVERITY_COLORS = {
  CRITICAL: { color: '#ef4444', bg: '#fef2f2', text: 'red' },
  HIGH:     { color: '#f97316', bg: '#fff7ed', text: 'orange' },
  MEDIUM:   { color: '#eab308', bg: '#fefce8', text: 'gold' },
  LOW:      { color: '#22c55e', bg: '#f0fdf4', text: 'green' },
};

// Status color mapping
const STATUS_COLORS = {
  INVESTIGATING: 'blue',
  RESOLVED:      'green',
  PENDING:       'orange',
  DISPUTED:      'purple',
  CLOSED:        'default',
};

// Violation type labels
const TYPE_LABELS = {
  THRESHOLD_BREACH: 'Threshold Breach',
  AVAILABILITY:     'Availability',
  LATENCY:          'Latency',
  PACKET_LOSS:      'Packet Loss',
  JITTER:           'Jitter',
};

const SeverityTag = ({ severity }) => {
  const config = SEVERITY_COLORS[severity] || { text: 'default' };
  return <Tag color={config.text}>{severity}</Tag>;
};

const StatusTag = ({ status }) => {
  const color = STATUS_COLORS[status] || 'default';
  return <Tag color={color}>{status}</Tag>;
};

const ViolationReporting = () => {
  // --- Data Hooks ---
  const { data: pendingData,  loading: pendingLoading  } = useMetabaseData(82, {});
  const { data: disputedData, loading: disputedLoading } = useMetabaseData(83, {});
  const { data: resolvedData, loading: resolvedLoading } = useMetabaseData(84, {});
  const { data: detailData,   loading: detailLoading   } = useMetabaseData(85, {});
  const { data: trendData,    loading: trendLoading    } = useMetabaseData(86, {});
  const { data: districtData, loading: districtLoading } = useMetabaseData(87, {});

  // --- KPI Values ---
  // Cards 82, 83, 84 return scalar: rows = [[value]]
  const pendingCount  = pendingData?.rows?.[0]?.[0]  ?? 0;
  const disputedCount = disputedData?.rows?.[0]?.[0] ?? 0;
  const resolvedCount = resolvedData?.rows?.[0]?.[0] ?? 0;

  // --- Card 85: Violation Detail Table columns ---
  // Columns: ID, ISP, Type, Severity, Division, District, Status, Detected At, Expected, Actual, Deviation %, Affected Subscribers
  const detailColumns = [
    {
      title: 'ID',
      dataIndex: 0,
      key: 'id',
      width: 60,
      fixed: 'left',
      sorter: (a, b) => (a[0] || 0) - (b[0] || 0),
    },
    {
      title: 'ISP',
      dataIndex: 1,
      key: 'isp',
      width: 160,
      fixed: 'left',
      sorter: (a, b) => (a[1] || '').localeCompare(b[1] || ''),
      ellipsis: true,
    },
    {
      title: 'Type',
      dataIndex: 2,
      key: 'type',
      width: 140,
      render: (val) => TYPE_LABELS[val] || val,
    },
    {
      title: 'Severity',
      dataIndex: 3,
      key: 'severity',
      width: 100,
      filters: [
        { text: 'CRITICAL', value: 'CRITICAL' },
        { text: 'HIGH',     value: 'HIGH' },
        { text: 'MEDIUM',   value: 'MEDIUM' },
        { text: 'LOW',      value: 'LOW' },
      ],
      onFilter: (value, record) => record[3] === value,
      render: (val) => <SeverityTag severity={val} />,
    },
    {
      title: 'Division',
      dataIndex: 4,
      key: 'division',
      width: 110,
    },
    {
      title: 'District',
      dataIndex: 5,
      key: 'district',
      width: 110,
    },
    {
      title: 'Status',
      dataIndex: 6,
      key: 'status',
      width: 130,
      filters: [
        { text: 'INVESTIGATING', value: 'INVESTIGATING' },
        { text: 'RESOLVED',      value: 'RESOLVED' },
        { text: 'PENDING',       value: 'PENDING' },
        { text: 'DISPUTED',      value: 'DISPUTED' },
      ],
      onFilter: (value, record) => record[6] === value,
      render: (val) => <StatusTag status={val} />,
    },
    {
      title: 'Detected At',
      dataIndex: 7,
      key: 'detectedAt',
      width: 150,
      sorter: (a, b) => new Date(a[7]) - new Date(b[7]),
      render: (val) => {
        if (!val) return '-';
        try {
          const d = new Date(val);
          return d.toLocaleString('en-BD', { timeZone: 'Asia/Dhaka', hour12: false });
        } catch {
          return val;
        }
      },
    },
    {
      title: 'Expected (Mbps)',
      dataIndex: 8,
      key: 'expected',
      width: 130,
      align: 'right',
      sorter: (a, b) => (a[8] || 0) - (b[8] || 0),
      render: (val) => (typeof val === 'number' ? val.toFixed(2) : val),
    },
    {
      title: 'Actual (Mbps)',
      dataIndex: 9,
      key: 'actual',
      width: 120,
      align: 'right',
      sorter: (a, b) => (a[9] || 0) - (b[9] || 0),
      render: (val) => (typeof val === 'number' ? val.toFixed(2) : val),
    },
    {
      title: 'Deviation %',
      dataIndex: 10,
      key: 'deviation',
      width: 110,
      align: 'right',
      sorter: (a, b) => (a[10] || 0) - (b[10] || 0),
      render: (val) => {
        const num = typeof val === 'number' ? val : parseFloat(val) || 0;
        const color = num > 20 ? '#ef4444' : num > 10 ? '#f97316' : '#22c55e';
        return (
          <span style={{ color, fontWeight: 600 }}>
            {num.toFixed(1)}%
          </span>
        );
      },
    },
    {
      title: 'Affected Subscribers',
      dataIndex: 11,
      key: 'subscribers',
      width: 150,
      align: 'right',
      sorter: (a, b) => (a[11] || 0) - (b[11] || 0),
      render: (val) => (val ? val.toLocaleString() : '0'),
    },
  ];

  const detailTableData = React.useMemo(() => {
    if (!detailData?.rows) return [];
    return detailData.rows.map((row, i) => ({
      key: `v-${i}`,
      0:  row[0],   // ID
      1:  row[1],   // ISP
      2:  row[2],   // Type
      3:  row[3],   // Severity
      4:  row[4],   // Division
      5:  row[5],   // District
      6:  row[6],   // Status
      7:  row[7],   // Detected At
      8:  row[8],   // Expected
      9:  row[9],   // Actual
      10: row[10],  // Deviation %
      11: row[11],  // Affected Subscribers
    }));
  }, [detailData]);

  // --- Card 86: Violation Trend by Severity (stacked bar) ---
  // Rows: [Date, Severity, Count] → transform to grouped by date
  const trendChartOption = React.useMemo(() => {
    if (!trendData?.rows || trendData.rows.length === 0) return null;

    const rows = trendData.rows;

    // Get unique dates (sorted)
    const dates = [...new Set(rows.map((r) => r[0]))].sort();

    // Get unique severities (preserve order: CRITICAL, HIGH, MEDIUM, LOW)
    const severityOrder = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    const severities = severityOrder.filter((s) =>
      rows.some((r) => r[1] === s)
    );

    // Build series data: for each severity, array of counts per date
    const seriesColors = {
      CRITICAL: '#ef4444',
      HIGH:     '#f97316',
      MEDIUM:   '#eab308',
      LOW:      '#22c55e',
    };

    const series = severities.map((sev) => {
      const values = dates.map((date) => {
        const found = rows.find((r) => r[0] === date && r[1] === sev);
        return found ? found[2] : 0;
      });
      return {
        name: sev,
        type: 'bar',
        stack: 'violations',
        data: values,
        itemStyle: { color: seriesColors[sev] },
        emphasis: { focus: 'series' },
      };
    });

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          let tooltip = `<strong>${params[0].axisValue}</strong><br/>`;
          params.forEach((p) => {
            if (p.value > 0) {
              const color = seriesColors[p.seriesName] || p.color;
              tooltip += `<span style="color:${color}">■</span> ${p.seriesName}: <strong>${p.value}</strong><br/>`;
            }
          });
          const total = params.reduce((sum, p) => sum + (p.value || 0), 0);
          tooltip += `<strong>Total: ${total}</strong>`;
          return tooltip;
        },
      },
      legend: {
        data: severities,
        bottom: 5,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 45,
          fontSize: 11,
          formatter: (val) => val.slice(5), // Show MM-DD only
        },
      },
      yAxis: {
        type: 'value',
        name: 'Violations',
        nameTextStyle: { fontSize: 12 },
        minInterval: 1,
      },
      series,
    };
  }, [trendData]);

  // --- Card 87: Violations by District table ---
  // Columns: Division, District, Total, Critical, High, Medium, Low
  const districtColumns = [
    {
      title: 'Division',
      dataIndex: 0,
      key: 'division',
      width: 110,
      sorter: (a, b) => (a[0] || '').localeCompare(b[0] || ''),
    },
    {
      title: 'District',
      dataIndex: 1,
      key: 'district',
      width: 120,
      sorter: (a, b) => (a[1] || '').localeCompare(b[1] || ''),
    },
    {
      title: 'Total',
      dataIndex: 2,
      key: 'total',
      width: 80,
      align: 'right',
      sorter: (a, b) => (a[2] || 0) - (b[2] || 0),
      defaultSortOrder: 'descend',
      render: (val) => (
        <span style={{ fontWeight: 700, color: val > 10 ? '#ef4444' : '#1f2937' }}>
          {val}
        </span>
      ),
    },
    {
      title: 'Critical',
      dataIndex: 3,
      key: 'critical',
      width: 80,
      align: 'right',
      sorter: (a, b) => (a[3] || 0) - (b[3] || 0),
      render: (val) => val > 0 ? <span style={{ color: '#ef4444', fontWeight: 600 }}>{val}</span> : <span style={{ color: '#999' }}>0</span>,
    },
    {
      title: 'High',
      dataIndex: 4,
      key: 'high',
      width: 70,
      align: 'right',
      sorter: (a, b) => (a[4] || 0) - (b[4] || 0),
      render: (val) => val > 0 ? <span style={{ color: '#f97316', fontWeight: 600 }}>{val}</span> : <span style={{ color: '#999' }}>0</span>,
    },
    {
      title: 'Medium',
      dataIndex: 5,
      key: 'medium',
      width: 80,
      align: 'right',
      sorter: (a, b) => (a[5] || 0) - (b[5] || 0),
      render: (val) => val > 0 ? <span style={{ color: '#eab308', fontWeight: 600 }}>{val}</span> : <span style={{ color: '#999' }}>0</span>,
    },
    {
      title: 'Low',
      dataIndex: 6,
      key: 'low',
      width: 70,
      align: 'right',
      sorter: (a, b) => (a[6] || 0) - (b[6] || 0),
      render: (val) => val > 0 ? <span style={{ color: '#22c55e', fontWeight: 600 }}>{val}</span> : <span style={{ color: '#999' }}>0</span>,
    },
  ];

  const districtTableData = React.useMemo(() => {
    if (!districtData?.rows) return [];
    return districtData.rows.map((row, i) => ({
      key: `d-${i}`,
      0: row[0], // Division
      1: row[1], // District
      2: row[2], // Total
      3: row[3], // Critical
      4: row[4], // High
      5: row[5], // Medium
      6: row[6], // Low
    }));
  }, [districtData]);

  // --- Render ---
  return (
    <div style={{ width: '100%', padding: '24px', background: '#f0f2f5', minHeight: '70vh' }}>

      {/* Page Header */}
      <Card bordered={false} style={{ marginBottom: 24 }} bodyStyle={{ padding: '20px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <WarningOutlined style={{ fontSize: 28, color: '#ef4444' }} />
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 'bold', margin: 0, color: '#1f2937' }}>
              Violation Reporting
            </h1>
            <p style={{ fontSize: 13, color: '#6b7280', margin: 0 }}>
              Detailed SLA violation analysis and reporting
            </p>
          </div>
        </div>
      </Card>

      {/* Row 1: KPI Scalar Cards (82, 83, 84) */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={8}>
          <ScalarCard
            title="Pending Violations"
            value={pendingCount}
            icon={<ExclamationCircleOutlined />}
            color="#f97316"
            subtitle="Violations awaiting action"
            loading={pendingLoading}
          />
        </Col>
        <Col xs={24} md={8}>
          <ScalarCard
            title="Active (Disputed)"
            value={disputedCount}
            icon={<WarningOutlined />}
            color="#8b5cf6"
            subtitle="Violations under dispute"
            loading={disputedLoading}
          />
        </Col>
        <Col xs={24} md={8}>
          <ScalarCard
            title="Resolved Violations"
            value={resolvedCount}
            icon={<CheckCircleOutlined />}
            color="#22c55e"
            subtitle="Successfully resolved cases"
            loading={resolvedLoading}
          />
        </Col>
      </Row>

      {/* Row 2: Violation Detail Table (Card 85) */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24}>
          <Card
            title={
              <span>
                <WarningOutlined style={{ marginRight: 8, color: '#ef4444' }} />
                R3.4 Violation Detail Table
                {detailData?.rows && (
                  <span style={{ fontSize: 12, color: '#888', fontWeight: 400, marginLeft: 12 }}>
                    ({detailData.rows.length} total violations)
                  </span>
                )}
              </span>
            }
            bordered={false}
          >
            {detailLoading ? (
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <Spin size="large" />
              </div>
            ) : !detailData?.rows?.length ? (
              <Alert message="No violation data available" type="info" showIcon />
            ) : (
              <DataTable
                columns={detailColumns}
                dataSource={detailTableData}
                loading={false}
                pageSize={10}
                scroll={{ x: 1400 }}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Row 3: Trend Chart (86) + District Breakdown (87) */}
      <Row gutter={[16, 16]}>
        {/* Card 86: Violation Trend by Severity */}
        <Col xs={24} lg={12}>
          <Card
            title="R3.5 Violation Trend by Severity"
            bordered={false}
            style={{ height: '100%' }}
          >
            {trendLoading ? (
              <div style={{ textAlign: 'center', padding: '80px 0' }}>
                <Spin size="large" />
              </div>
            ) : trendChartOption ? (
              <ReactECharts
                option={trendChartOption}
                style={{ height: '380px', width: '100%' }}
                notMerge={true}
                lazyUpdate={true}
              />
            ) : (
              <Alert message="No trend data available" type="info" showIcon />
            )}
          </Card>
        </Col>

        {/* Card 87: Violations by District */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                R3.6 Violations by District
                {districtData?.rows && (
                  <span style={{ fontSize: 12, color: '#888', fontWeight: 400, marginLeft: 12 }}>
                    ({districtData.rows.length} districts)
                  </span>
                )}
              </span>
            }
            bordered={false}
            style={{ height: '100%' }}
          >
            {districtLoading ? (
              <div style={{ textAlign: 'center', padding: '80px 0' }}>
                <Spin size="large" />
              </div>
            ) : !districtData?.rows?.length ? (
              <Alert message="No district data available" type="info" showIcon />
            ) : (
              <DataTable
                columns={districtColumns}
                dataSource={districtTableData}
                loading={false}
                pageSize={10}
                scroll={{ x: 600 }}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ViolationReporting;
