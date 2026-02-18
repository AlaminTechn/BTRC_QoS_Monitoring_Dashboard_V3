/**
 * Data transformation utilities
 * Convert Metabase data format to ECharts/Leaflet format
 */

/**
 * Transform Metabase data to ECharts bar chart format
 * @param {Array} rows - Metabase rows [[name, value], ...]
 * @param {Array} columns - Column definitions
 * @returns {object} {categories: [], values: []}
 */
export const transformToBarChart = (rows, columns) => {
  if (!rows || rows.length === 0) {
    return { categories: [], values: [] };
  }

  return {
    categories: rows.map((row) => row[0]),
    values: rows.map((row) => row[1]),
  };
};

/**
 * Transform Metabase data to ECharts line chart format
 * @param {Array} rows - Metabase rows [[date, value], ...]
 * @returns {object} {dates: [], values: []}
 */
export const transformToLineChart = (rows) => {
  if (!rows || rows.length === 0) {
    return { dates: [], values: [] };
  }

  return {
    dates: rows.map((row) => row[0]),
    values: rows.map((row) => row[1]),
  };
};

/**
 * Transform Metabase data to table format
 * @param {Array} rows - Metabase rows
 * @param {Array} columns - Column definitions
 * @returns {Array} Table data with keys
 */
export const transformToTable = (rows, columns) => {
  if (!rows || rows.length === 0) {
    return [];
  }

  return rows.map((row, index) => {
    const record = { key: index };
    columns.forEach((col, colIndex) => {
      record[col.name] = row[colIndex];
    });
    return record;
  });
};

/**
 * Transform Metabase data to Leaflet GeoJSON format
 * @param {Array} rows - Metabase rows [[name, value], ...]
 * @param {object} geoJson - GeoJSON feature collection
 * @param {string} nameKey - Property key for matching (e.g., 'shapeName' or 'shapeISO')
 * @returns {object} GeoJSON with properties
 */
export const transformToGeoJSON = (rows, geoJson, nameKey = 'shapeName') => {
  if (!rows || rows.length === 0 || !geoJson) {
    return geoJson;
  }

  // Create a map of name -> value
  const dataMap = {};
  rows.forEach((row) => {
    dataMap[row[0]] = row[1];
  });

  // Clone GeoJSON and add data to properties
  const enhancedGeoJSON = JSON.parse(JSON.stringify(geoJson));

  enhancedGeoJSON.features.forEach((feature) => {
    const name = feature.properties[nameKey];
    if (name && dataMap[name] !== undefined) {
      feature.properties.value = dataMap[name];
    } else {
      feature.properties.value = 0;
    }
  });

  return enhancedGeoJSON;
};

/**
 * GeoJSON name mappings (from MEMORY.md)
 * Maps database names to GeoJSON names
 */
export const DIVISION_NAME_MAPPING = {
  Chattagram: 'Chittagong',
  Rajshahi: 'Rajshani',
};

export const DISTRICT_NAME_MAPPING = {
  Bogura: 'Bogra',
  Brahmanbaria: 'Brahamanbaria',
  Chapainawabganj: 'Nawabganj',
  Chattogram: 'Chittagong',
  Coxsbazar: "Cox's Bazar",
  Jashore: 'Jessore',
  Jhalakathi: 'Jhalokati',
  Moulvibazar: 'Maulvibazar',
  Netrokona: 'Netrakona',
};

/**
 * Apply name mapping to data rows
 * @param {Array} rows - Metabase rows
 * @param {object} mapping - Name mapping object
 * @returns {Array} Mapped rows
 */
export const applyNameMapping = (rows, mapping) => {
  return rows.map((row) => {
    const name = row[0];
    const mappedName = mapping[name] || name;
    return [mappedName, ...row.slice(1)];
  });
};

/**
 * Get color for value based on thresholds
 * @param {number} value - Numeric value
 * @param {object} thresholds - {low: 30, medium: 60, high: 100}
 * @returns {string} Color code
 */
export const getColorForValue = (value, thresholds = { low: 30, medium: 60 }) => {
  if (value < thresholds.low) {
    return '#ef4444'; // Red
  } else if (value < thresholds.medium) {
    return '#f59e0b'; // Orange
  } else {
    return '#10b981'; // Green
  }
};

/**
 * Format percentage
 * @param {number} value - Numeric value
 * @returns {string} Formatted percentage
 */
export const formatPercentage = (value) => {
  return `${value.toFixed(1)}%`;
};

/**
 * Format speed (Mbps)
 * @param {number} value - Speed in Mbps
 * @returns {string} Formatted speed
 */
export const formatSpeed = (value) => {
  return `${value.toFixed(2)} Mbps`;
};
