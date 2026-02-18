/**
 * Regional Analysis Dashboard (Tab R2.2)
 * Main page component for Regional Analysis
 */

import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Spin, Alert, Breadcrumb, Space, Divider } from 'antd';
import { HomeOutlined, EnvironmentOutlined, DatabaseOutlined } from '@ant-design/icons';
import ChoroplethMap from '../components/maps/ChoroplethMap';
import BarChart from '../components/charts/BarChart';
import DataTable from '../components/charts/DataTable';
import FilterPanel from '../components/filters/FilterPanel';
import useMetabaseData from '../hooks/useMetabaseData';
import {
  transformToBarChart,
  transformToTable,
  transformToGeoJSON,
  applyNameMapping,
  DIVISION_NAME_MAPPING,
  DISTRICT_NAME_MAPPING,
} from '../utils/dataTransform';

const RegionalAnalysis = () => {
  // Filter state
  const [filters, setFilters] = useState({
    division: undefined,
    district: undefined,
    isp: undefined,
  });

  // GeoJSON data
  const [divisionGeoJSON, setDivisionGeoJSON] = useState(null);
  const [districtGeoJSON, setDistrictGeoJSON] = useState(null);

  // Fetch violation data (Card 87)
  // Data format: [Division, District, Total, Critical, High, Medium, Low]
  const {
    data: violationData,
    loading: dataLoading,
    error: dataError,
  } = useMetabaseData(87, filters);

  // Aggregate data for divisions (sum by division)
  const divisionData = React.useMemo(() => {
    if (!violationData || !violationData.rows) return null;

    const divisionMap = {};
    violationData.rows.forEach((row) => {
      const division = row[0]; // Division name
      const total = row[2]; // Total violations

      if (!divisionMap[division]) {
        divisionMap[division] = 0;
      }
      divisionMap[division] += total;
    });

    // Convert to array format [[Division, Total], ...]
    const rows = Object.entries(divisionMap).map(([division, total]) => [division, total]);

    return {
      rows,
      columns: [
        { name: 'Division', displayName: 'Division', type: 'type/Text' },
        { name: 'Total', displayName: 'Total Violations', type: 'type/BigInteger' },
      ],
      metadata: { rowCount: rows.length },
    };
  }, [violationData]);

  // District data (use raw data)
  const districtData = React.useMemo(() => {
    if (!violationData || !violationData.rows) return null;

    // If division filter is set, filter districts
    let rows = violationData.rows;
    if (filters.division) {
      rows = rows.filter((row) => row[0] === filters.division);
    }

    // Format: [District, Total]
    const districtRows = rows.map((row) => [row[1], row[2]]);

    return {
      rows: districtRows,
      columns: [
        { name: 'District', displayName: 'District', type: 'type/Text' },
        { name: 'Total', displayName: 'Total Violations', type: 'type/BigInteger' },
      ],
      metadata: { rowCount: districtRows.length },
    };
  }, [violationData, filters.division]);

  // Load GeoJSON files
  useEffect(() => {
    const loadGeoJSON = async () => {
      try {
        // Division GeoJSON (use local file)
        const divPath = import.meta.env.VITE_GEOJSON_DIVISIONS || '/geodata/bangladesh_divisions_8.geojson';
        console.log('Loading division GeoJSON from:', divPath);
        const divResponse = await fetch(divPath);

        if (!divResponse.ok) {
          throw new Error(`Failed to load division GeoJSON: ${divResponse.status} ${divResponse.statusText}`);
        }

        const divGeoJSON = await divResponse.json();
        console.log('Division GeoJSON loaded:', divGeoJSON.features?.length, 'features');
        setDivisionGeoJSON(divGeoJSON);

        // District GeoJSON (use local file)
        const distPath = import.meta.env.VITE_GEOJSON_DISTRICTS || '/geodata/bgd_districts.geojson';
        console.log('Loading district GeoJSON from:', distPath);
        const distResponse = await fetch(distPath);

        if (!distResponse.ok) {
          throw new Error(`Failed to load district GeoJSON: ${distResponse.status} ${distResponse.statusText}`);
        }

        const distGeoJSON = await distResponse.json();
        console.log('District GeoJSON loaded:', distGeoJSON.features?.length, 'features');
        setDistrictGeoJSON(distGeoJSON);
      } catch (error) {
        console.error('Failed to load GeoJSON:', error);
        alert(`GeoJSON Loading Error: ${error.message}\n\nPlease ensure geodata files are in the public/geodata/ folder.`);
      }
    };

    loadGeoJSON();
  }, []);

  // Transform data for charts
  const divisionChartData =
    divisionData && divisionData.rows
      ? transformToBarChart(divisionData.rows, divisionData.columns)
      : { categories: [], values: [] };

  const districtChartData =
    districtData && districtData.rows
      ? transformToBarChart(districtData.rows, districtData.columns)
      : { categories: [], values: [] };

  // Transform data for tables
  const divisionTableData =
    divisionData && divisionData.rows
      ? divisionData.rows.map((row, index) => ({
          key: `div-${index}`,
          0: row[0], // Division name
          1: row[1], // Total violations
        }))
      : [];

  const districtTableData =
    districtData && districtData.rows
      ? districtData.rows.map((row, index) => ({
          key: `dist-${index}`,
          0: row[0], // District name
          1: row[1], // Total violations
        }))
      : [];

  // Transform data for maps
  const divisionMapData =
    divisionData && divisionData.rows && divisionGeoJSON
      ? transformToGeoJSON(
          applyNameMapping(divisionData.rows, DIVISION_NAME_MAPPING),
          divisionGeoJSON,
          'shapeName'
        )
      : null;

  const districtMapData =
    districtData && districtData.rows && districtGeoJSON
      ? transformToGeoJSON(
          applyNameMapping(districtData.rows, DISTRICT_NAME_MAPPING),
          districtGeoJSON,
          'shapeName'
        )
      : null;

  // Get unique divisions, districts, ISPs for filters
  const divisions = divisionData?.rows
    ? [...new Set(divisionData.rows.map((row) => row[0]))].sort()
    : [];

  const districts = districtData?.rows
    ? [...new Set(districtData.rows.map((row) => row[0]))].sort()
    : [];

  const isps = []; // ISP data would come from a separate card

  // Handle filter changes
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleFilterReset = () => {
    setFilters({
      division: undefined,
      district: undefined,
      isp: undefined,
    });
  };

  // Handle region click on map
  const handleDivisionClick = (feature) => {
    const divisionName = feature.properties.shapeName || feature.properties.name;
    // Reverse mapping
    const dbName =
      Object.keys(DIVISION_NAME_MAPPING).find(
        (key) => DIVISION_NAME_MAPPING[key] === divisionName
      ) || divisionName;
    setFilters({ ...filters, division: dbName, district: undefined });
  };

  const handleDistrictClick = (feature) => {
    const districtName = feature.properties.shapeName || feature.properties.name;
    // Reverse mapping
    const dbName =
      Object.keys(DISTRICT_NAME_MAPPING).find(
        (key) => DISTRICT_NAME_MAPPING[key] === districtName
      ) || districtName;
    setFilters({ ...filters, district: dbName });
  };

  // Handle bar click
  const handleBarClick = (data) => {
    if (!filters.division) {
      // Clicked on division bar
      setFilters({ ...filters, division: data.name, district: undefined });
    } else {
      // Clicked on district bar
      setFilters({ ...filters, district: data.name });
    }
  };

  // Table columns
  const divisionColumns = [
    { title: 'Division', dataIndex: 0, key: 'division', width: 150 },
    {
      title: 'Total Violations',
      dataIndex: 1,
      key: 'total',
      width: 150,
      render: (value) => value || 0,
    },
  ];

  const districtColumns = [
    { title: 'District', dataIndex: 0, key: 'district', width: 150 },
    {
      title: 'Total Violations',
      dataIndex: 1,
      key: 'total',
      width: 150,
      render: (value) => value || 0,
    },
  ];

  return (
    <div style={{ background: '#f0f2f5', width: '100%', minHeight: '70vh' }}>
      {/* Page Container - Full Width */}
      <div style={{ width: '100%', padding: '32px' }}>

        {/* Breadcrumb Navigation */}
        <Breadcrumb style={{ marginBottom: 16, marginTop: 16 }}>
          <Breadcrumb.Item>
            <HomeOutlined />
            <span style={{ marginLeft: 8 }}>Home</span>
          </Breadcrumb.Item>
          <Breadcrumb.Item>
            <DatabaseOutlined />
            <span style={{ marginLeft: 8 }}>Regulatory Dashboard</span>
          </Breadcrumb.Item>
          <Breadcrumb.Item>
            <EnvironmentOutlined />
            <span style={{ marginLeft: 8 }}>Regional Analysis</span>
          </Breadcrumb.Item>
          {filters.division && (
            <Breadcrumb.Item>{filters.division}</Breadcrumb.Item>
          )}
          {filters.district && (
            <Breadcrumb.Item>{filters.district}</Breadcrumb.Item>
          )}
        </Breadcrumb>

        {/* Page Header */}
        <Card
          bordered={false}
          style={{ marginBottom: 24 }}
          bodyStyle={{ padding: '24px 32px' }}
        >
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <h1 style={{
              fontSize: 28,
              fontWeight: 'bold',
              margin: 0,
              color: '#1f2937'
            }}>
              Regional Violation Analysis
            </h1>
            <p style={{
              fontSize: 14,
              color: '#6b7280',
              margin: 0
            }}>
              SLA violation distribution across divisions and districts
            </p>
          </Space>
        </Card>

        {/* Filters */}
        <div style={{ marginBottom: 24 }}>
          <FilterPanel
            filters={filters}
            onFilterChange={handleFilterChange}
            onReset={handleFilterReset}
            divisions={divisions}
            districts={districts}
            isps={isps}
            loading={dataLoading}
          />
        </div>

        {/* Error alerts */}
        {dataError && (
          <Alert
            message="Error Loading Data"
            description={dataError?.message}
            type="error"
            closable
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}

        {/* Division Level */}
        {!filters.division && (
          <>
            {/* Section Header */}
            <div style={{ marginBottom: 24 }}>
              <Divider orientation="left" style={{ fontSize: 20, fontWeight: 'bold' }}>
                Division Level Analysis
              </Divider>
              <p style={{ color: '#6b7280', marginLeft: 24, marginTop: -12 }}>
                Overview of violations across all 8 divisions
              </p>
            </div>

            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card
                  title="Division Violation Map"
                  bordered={false}
                  bodyStyle={{ padding: '24px' }}
                  style={{ height: '100%', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                >
                  {dataLoading ? (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" />
                    </div>
                  ) : (
                    <ChoroplethMap
                      geojson={divisionMapData}
                      title="Division Violations"
                      onRegionClick={handleDivisionClick}
                      height="500px"
                    />
                  )}
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card
                  title="Division Violation Ranking"
                  bordered={false}
                  bodyStyle={{ padding: '24px' }}
                  style={{ height: '100%', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                >
                  {dataLoading ? (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" />
                    </div>
                  ) : (
                    <BarChart
                      categories={divisionChartData.categories}
                      values={divisionChartData.values}
                      title="Total Violations by Division"
                      yAxisLabel="Total Violations"
                      seriesName="Violations"
                      onBarClick={handleBarClick}
                      height={500}
                      color="#ef4444"
                    />
                  )}
                </Card>
              </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
              <Col xs={24}>
                <Card
                  title="Division Violation Summary"
                  bordered={false}
                  bodyStyle={{ padding: '24px' }}
                  style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                >
                <DataTable
                  columns={divisionColumns}
                  dataSource={divisionTableData}
                  loading={dataLoading}
                  pageSize={8}
                  showPagination={false}
                />
              </Card>
            </Col>
          </Row>
        </>
        )}

        {/* District Level */}
        {filters.division && (
          <>
            {/* Section Header */}
            <div style={{ marginBottom: 24 }}>
              <Divider orientation="left" style={{ fontSize: 20, fontWeight: 'bold' }}>
                District Level Analysis - {filters.division}
              </Divider>
              <p style={{ color: '#6b7280', marginLeft: 24, marginTop: -12 }}>
                Detailed violations breakdown by district in {filters.division} division
              </p>
            </div>

            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card
                  title="District Violation Map"
                  bordered={false}
                  bodyStyle={{ padding: '24px' }}
                  style={{ height: '100%', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                >
                  {dataLoading ? (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" />
                    </div>
                  ) : (
                    <ChoroplethMap
                      geojson={districtMapData}
                      title={`Districts in ${filters.division}`}
                      onRegionClick={handleDistrictClick}
                      height="500px"
                    />
                  )}
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card
                  title="District Violation Ranking"
                  bordered={false}
                  bodyStyle={{ padding: '24px' }}
                  style={{ height: '100%', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                >
                  {dataLoading ? (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" />
                    </div>
                  ) : (
                    <BarChart
                      categories={districtChartData.categories}
                      values={districtChartData.values}
                      title={`Total Violations by District (${filters.division})`}
                      yAxisLabel="Total Violations"
                      seriesName="Violations"
                      onBarClick={handleBarClick}
                      height={500}
                      color="#ef4444"
                    />
                  )}
                </Card>
              </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
              <Col xs={24}>
                <Card
                  title="District Violation Summary"
                  bordered={false}
                  bodyStyle={{ padding: '24px' }}
                  style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                >
                <DataTable
                  columns={districtColumns}
                  dataSource={districtTableData}
                  loading={dataLoading}
                  pageSize={10}
                />
              </Card>
            </Col>
          </Row>
        </>
        )}

      </div>
      {/* End Page Container */}
    </div>
  );
};

export default RegionalAnalysis;
