/**
 * BTRC QoS Dashboard - Custom Drill-Down Handler
 * Wraps Metabase dashboard and adds click-to-navigate functionality
 */

// Configuration
const CONFIG = {
    metabaseUrl: 'http://localhost:8080',  // Use nginx proxy (same origin)
    dashboardId: 6,

    // Tab IDs for navigation
    tabs: {
        sla: 13,         // R2.1: SLA Monitoring
        regional: 14,    // R2.2: Regional Analysis
        violations: 15   // R2.3: Violation Reporting
    },

    // Known values for validation
    divisions: ['Dhaka', 'Chattagram', 'Khulna', 'Rajshahi', 'Barisal', 'Sylhet', 'Rangpur', 'Mymensingh'],

    // Districts by division (for click detection)
    districts: {
        'Dhaka': ['Dhaka', 'Faridpur', 'Gazipur', 'Gopalganj', 'Kishoreganj', 'Madaripur',
                  'Manikganj', 'Munshiganj', 'Narayanganj', 'Narsingdi', 'Rajbari', 'Shariatpur', 'Tangail'],
        'Chattagram': ['Bandarban', 'Brahmanbaria', 'Chandpur', 'Chattogram', 'Comilla', 'Coxsbazar',
                       'Feni', 'Khagrachhari', 'Lakshmipur', 'Noakhali', 'Rangamati'],
        'Khulna': ['Bagerhat', 'Chuadanga', 'Jashore', 'Jhenaidah', 'Khulna', 'Kushtia',
                   'Magura', 'Meherpur', 'Narail', 'Satkhira'],
        'Rajshahi': ['Bogura', 'Joypurhat', 'Naogaon', 'Natore', 'Chapainawabganj', 'Pabna',
                     'Rajshahi', 'Sirajganj'],
        'Barisal': ['Barguna', 'Barisal', 'Bhola', 'Jhalakathi', 'Patuakhali', 'Pirojpur'],
        'Sylhet': ['Habiganj', 'Moulvibazar', 'Sunamganj', 'Sylhet'],
        'Rangpur': ['Dinajpur', 'Gaibandha', 'Kurigram', 'Lalmonirhat', 'Nilphamari',
                    'Panchagarh', 'Rangpur', 'Thakurgaon'],
        'Mymensingh': ['Jamalpur', 'Mymensingh', 'Netrokona', 'Sherpur']
    }
};

// Global state for drill-down menu
let drillDownState = {
    division: null,
    district: null,
    type: null  // 'division' or 'district'
};

// Show drill-down menu
function showDrillDownMenu(division, district = null) {
    drillDownState.division = division;
    drillDownState.district = district;
    drillDownState.type = district ? 'district' : 'division';

    const menu = document.getElementById('drill-down-menu');
    const overlay = document.getElementById('drill-down-overlay');
    const title = document.getElementById('drill-down-title');

    if (district) {
        title.textContent = `Drill into ${district} District`;
    } else {
        title.textContent = `Drill into ${division} Division`;
    }

    menu.classList.add('show');
    overlay.classList.add('show');
}

// Close drill-down menu
function closeDrillDownMenu() {
    const menu = document.getElementById('drill-down-menu');
    const overlay = document.getElementById('drill-down-overlay');

    menu.classList.remove('show');
    overlay.classList.remove('show');

    drillDownState = { division: null, district: null, type: null };
}

// Navigate to specific tab with drill-down
function drillDownTo(tab) {
    const tabId = CONFIG.tabs[tab];
    const { division, district } = drillDownState;

    let newUrl = `/dashboard?`;
    const params = [];

    if (division) {
        params.push(`division=${encodeURIComponent(division)}`);
    }
    if (district) {
        params.push(`district=${encodeURIComponent(district)}`);
    }
    params.push(`tab=${tabId}`);

    newUrl += params.join('&');

    console.log(`🔹 Navigating to ${tab} tab:`, newUrl);

    window.history.pushState({ division, district, tab }, '', newUrl);
    closeDrillDownMenu();
    updateBreadcrumb();
    loadDashboard();
}

// Parse URL parameters
function getURLParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        division: params.get('division'),
        district: params.get('district'),
        isp: params.get('isp'),
        tab: params.get('tab')
    };
}

// Build Metabase URL with current filters
function buildMetabaseURL() {
    const params = getURLParams();
    let url = `${CONFIG.metabaseUrl}/dashboard/${CONFIG.dashboardId}`;
    const queryParams = [];

    if (params.division) {
        queryParams.push(`division=${encodeURIComponent(params.division)}`);
    }
    if (params.district) {
        queryParams.push(`district=${encodeURIComponent(params.district)}`);
    }
    if (params.isp) {
        queryParams.push(`isp=${encodeURIComponent(params.isp)}`);
    }

    // Add tab parameter if specified in URL, otherwise default to R2.2
    const tabId = params.tab || CONFIG.tabs.regional;
    if (queryParams.length > 0) {
        url += '?' + queryParams.join('&') + `&tab=${tabId}`;
    } else {
        url += `?tab=${tabId}`;
    }

    return url;
}

// Update breadcrumb based on current drill-down level
function updateBreadcrumb() {
    const params = getURLParams();
    const breadcrumb = document.getElementById('breadcrumb');
    const resetBtn = document.getElementById('reset-btn');

    let html = '<a href="/dashboard" title="View all divisions">🏠 National</a>';
    let hasFilters = false;

    if (params.division) {
        html += '<span class="breadcrumb-separator">➜</span>';
        html += `<a href="/dashboard?division=${encodeURIComponent(params.division)}" title="View districts in ${params.division}">📍 ${params.division}</a>`;
        hasFilters = true;
    }

    if (params.district) {
        html += '<span class="breadcrumb-separator">➜</span>';
        html += `<a href="/dashboard?division=${encodeURIComponent(params.division)}&district=${encodeURIComponent(params.district)}" title="View ISPs in ${params.district}">🏘️ ${params.district}</a>`;
    }

    if (params.isp) {
        html += '<span class="breadcrumb-separator">➜</span>';
        html += `<span class="breadcrumb-current" title="Current ISP">🏢 ${params.isp}</span>`;
    }

    breadcrumb.innerHTML = html;

    // Show/hide reset button
    if (hasFilters) {
        resetBtn.classList.add('visible');
    } else {
        resetBtn.classList.remove('visible');
    }
}

// Reset dashboard to national view
function resetDashboard() {
    window.history.pushState({}, '', '/dashboard');
    updateBreadcrumb();
    loadDashboard();
}

// Load Metabase dashboard
function loadDashboard() {
    const iframe = document.getElementById('dashboard-container');
    const loading = document.getElementById('loading');
    const url = buildMetabaseURL();

    console.log('Loading Metabase:', url);

    // Show loading indicator
    loading.classList.remove('hide');

    // Set iframe source
    iframe.src = url;

    // Hide loading when iframe loads
    iframe.onload = function() {
        setTimeout(() => {
            loading.classList.add('hide');
        }, 500);

        // Try to inject click handlers (may fail due to CORS)
        injectClickHandlers();
    };

    // Update breadcrumb
    updateBreadcrumb();

    // Update page title
    const params = getURLParams();
    if (params.isp) {
        document.title = `${params.isp} - BTRC QoS Dashboard`;
    } else if (params.district) {
        document.title = `${params.district} - BTRC QoS Dashboard`;
    } else if (params.division) {
        document.title = `${params.division} - BTRC QoS Dashboard`;
    } else {
        document.title = 'BTRC QoS Dashboard - Regulatory Operations';
    }
}

// Inject click handlers into Metabase iframe (if possible)
function injectClickHandlers() {
    const iframe = document.getElementById('dashboard-container');

    try {
        // Try to access iframe content (same-origin now, should work)
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

        if (!iframeDoc) {
            console.warn('Cannot access iframe content (CORS restriction)');
            return;
        }

        console.log('✓ Iframe content accessible (same-origin)');

        // Use MutationObserver to detect when tables are rendered
        let attemptCount = 0;
        const maxAttempts = 20;

        const checkInterval = setInterval(() => {
            attemptCount++;

            const tables = iframeDoc.querySelectorAll('table');
            console.log(`Attempt ${attemptCount}: Found ${tables.length} tables`);

            if (tables.length > 0) {
                console.log('✓ Tables found, attaching click handlers...');
                clearInterval(checkInterval);
                attachTableClickHandlers(iframeDoc);
            } else if (attemptCount >= maxAttempts) {
                console.warn('⚠ No tables found after 20 attempts');
                clearInterval(checkInterval);
            }
        }, 500);  // Check every 500ms

    } catch (e) {
        console.warn('Cannot inject click handlers:', e.message);
        console.info('Fallback: Use Metabase filters manually, then copy URL to share');
    }
}

// Attach click handlers to table cells
function attachTableClickHandlers(iframeDoc) {
    const params = getURLParams();
    const tables = iframeDoc.querySelectorAll('table');

    console.log(`Found ${tables.length} tables in iframe`);

    let clickableCount = 0;

    tables.forEach((table, tableIndex) => {
        const rows = table.querySelectorAll('tbody tr');
        console.log(`Table ${tableIndex + 1}: ${rows.length} rows`);

        rows.forEach((row, rowIndex) => {
            const cells = row.querySelectorAll('td');

            cells.forEach((cell, cellIndex) => {
                const text = cell.textContent.trim();

                // National level: Make division names clickable
                if (!params.division && CONFIG.divisions.includes(text)) {
                    cell.style.cursor = 'pointer';
                    cell.style.color = '#2b6cb0';
                    cell.style.fontWeight = '600';
                    cell.title = `Click to drill-down to ${text}`;

                    // Remove existing listeners
                    const newCell = cell.cloneNode(true);
                    cell.parentNode.replaceChild(newCell, cell);

                    newCell.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`🔹 Division clicked: ${text}`);

                        // Show drill-down menu
                        showDrillDownMenu(text);
                    });

                    clickableCount++;
                    console.log(`✓ Made clickable: Division "${text}" in table ${tableIndex + 1}, row ${rowIndex + 1}`);
                }

                // Division level: Make district names clickable
                if (params.division && !params.district) {
                    const divisionDistricts = CONFIG.districts[params.division] || [];
                    if (divisionDistricts.includes(text)) {
                        cell.style.cursor = 'pointer';
                        cell.style.color = '#2b6cb0';
                        cell.style.fontWeight = '600';
                        cell.title = `Click to drill-down to ${text}`;

                        // Remove existing listeners
                        const newCell = cell.cloneNode(true);
                        cell.parentNode.replaceChild(newCell, cell);

                        newCell.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            console.log(`🔹 District clicked: ${text}`);

                            // Show drill-down menu for district
                            showDrillDownMenu(params.division, text);
                        });

                        clickableCount++;
                        console.log(`✓ Made clickable: District "${text}" in table ${tableIndex + 1}, row ${rowIndex + 1}`);
                    }
                }
            });
        });
    });

    console.log(`✅ Total clickable cells: ${clickableCount}`);

    if (clickableCount === 0) {
        console.warn('⚠️ No clickable cells found! Check if division/district names match CONFIG');
        console.log('Expected divisions:', CONFIG.divisions);
        if (params.division) {
            console.log('Expected districts for', params.division + ':', CONFIG.districts[params.division]);
        }
    }

    // Also attach click handlers to maps (SVG regions)
    attachMapClickHandlers(iframeDoc);
}

// Attach click handlers to choropleth map regions
function attachMapClickHandlers(iframeDoc) {
    const params = getURLParams();

    // Find all SVG elements (maps)
    const svgs = iframeDoc.querySelectorAll('svg');
    console.log(`Found ${svgs.length} SVG maps`);

    let mapClickCount = 0;

    svgs.forEach((svg, svgIndex) => {
        // Find all path elements (map regions)
        const paths = svg.querySelectorAll('path[data-testid], path[class*="region"], path[fill]');

        paths.forEach((path, pathIndex) => {
            // Try to get region name from various attributes
            const regionName =
                path.getAttribute('data-region') ||
                path.getAttribute('aria-label') ||
                path.getAttribute('title') ||
                path.getAttribute('data-name');

            // Check if this is a division region
            if (!params.division && regionName && CONFIG.divisions.includes(regionName)) {
                path.style.cursor = 'pointer';
                path.style.transition = 'opacity 0.2s';

                const originalOpacity = path.style.opacity || '1';

                path.addEventListener('mouseenter', function() {
                    this.style.opacity = '0.8';
                });

                path.addEventListener('mouseleave', function() {
                    this.style.opacity = originalOpacity;
                });

                path.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`🗺️ Map region clicked: ${regionName}`);
                    showDrillDownMenu(regionName);
                });

                mapClickCount++;
                console.log(`✓ Made clickable: Map region "${regionName}"`);
            }

            // Check if this is a district region
            if (params.division && !params.district && regionName) {
                const divisionDistricts = CONFIG.districts[params.division] || [];
                if (divisionDistricts.includes(regionName)) {
                    path.style.cursor = 'pointer';
                    path.style.transition = 'opacity 0.2s';

                    const originalOpacity = path.style.opacity || '1';

                    path.addEventListener('mouseenter', function() {
                        this.style.opacity = '0.8';
                    });

                    path.addEventListener('mouseleave', function() {
                        this.style.opacity = originalOpacity;
                    });

                    path.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`🗺️ Map region clicked: ${regionName}`);
                        showDrillDownMenu(params.division, regionName);
                    });

                    mapClickCount++;
                    console.log(`✓ Made clickable: Map region "${regionName}"`);
                }
            }
        });
    });

    console.log(`✅ Total clickable map regions: ${mapClickCount}`);
}

// Listen for messages from Metabase (alternative to iframe injection)
window.addEventListener('message', function(event) {
    // Check if message is from Metabase
    if (event.origin !== CONFIG.metabaseUrl) {
        return;
    }

    const data = event.data;

    // Handle click events from Metabase
    if (data.type === 'metabase:click' || data.type === 'drill-down') {
        const { column, value } = data;
        const params = getURLParams();

        console.log('Metabase click event:', column, value);

        // Build navigation URL based on clicked value
        if (CONFIG.divisions.includes(value)) {
            window.location.href = `/dashboard?division=${encodeURIComponent(value)}`;
        } else if (params.division) {
            const divisionDistricts = CONFIG.districts[params.division] || [];
            if (divisionDistricts.includes(value)) {
                window.location.href = `/dashboard?division=${encodeURIComponent(params.division)}&district=${encodeURIComponent(value)}`;
            }
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // ESC: Close drill-down menu
    if (e.key === 'Escape') {
        const menu = document.getElementById('drill-down-menu');
        if (menu && menu.classList.contains('show')) {
            e.preventDefault();
            closeDrillDownMenu();
        }
    }

    // Alt + Home: Reset to national view
    if (e.altKey && e.key === 'Home') {
        e.preventDefault();
        resetDashboard();
    }

    // Alt + Backspace: Go back one level
    if (e.altKey && e.key === 'Backspace') {
        e.preventDefault();
        window.history.back();
    }
});

// Handle browser back/forward
window.addEventListener('popstate', function(event) {
    console.log('Navigation (back/forward) detected, reloading dashboard');
    loadDashboard();
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('BTRC QoS Dashboard - Custom Drill-Down Initialized');
    console.log('Current URL:', window.location.href);
    console.log('Parameters:', getURLParams());

    loadDashboard();

    // Hide info banner after 10 seconds
    setTimeout(() => {
        const banner = document.getElementById('info-banner');
        if (banner) {
            banner.style.transition = 'opacity 0.5s';
            banner.style.opacity = '0';
            setTimeout(() => banner.remove(), 500);
        }
    }, 10000);
});

// Reload dashboard when hash changes (for future use)
window.addEventListener('hashchange', function() {
    loadDashboard();
});

console.log('✅ Dashboard script loaded');
