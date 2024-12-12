// Feature flags
const CONFIG = {
    enableTimeline: false  // Set to true to enable timeline feature
};

// Chart configuration
let gdpChart = null;
let stablecoinsDistributionChart = null;
let testChart = null;

// Global variables to track sorting state
let protocolSortConfig = { column: 'tvl', direction: 'desc' };
let yieldSortConfig = { column: 'apy', direction: 'desc' };

function initializeChart() {
    const ctx = document.getElementById('gdp-chart').getContext('2d');
    const showTimeline = CONFIG.enableTimeline;
    gdpChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'GDP',
                data: [],
                borderColor: '#627EEA',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(98, 126, 234, 0.1)',
                borderWidth: 2,
                pointRadius: showTimeline ? 1 : 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: showTimeline
                }
            },
            scales: {
                y: {
                    display: showTimeline,
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff',
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                },
                x: {
                    display: showTimeline,
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#fff',
                        maxRotation: 0,
                        maxTicksLimit: 6
                    }
                }
            }
        }
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        notation: 'compact',
        maximumFractionDigits: 2
    }).format(num);
}

function formatChange(current, previous) {
    if (!previous) return '--';
    const change = ((current - previous) / previous) * 100;
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
}

function updateGDP() {
    fetch('/api/gdp')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update main GDP value
            document.getElementById('gdp-value').textContent = formatNumber(data.gdp);
            
            // Update GDP 24h change
            const gdpChange = data.change_24h;
            document.getElementById('gdp-change').innerHTML = 
                `24h Change: ${formatPercentage(gdpChange)}`;
            
            // Update components
            const components = data.components;
            Object.entries(components).forEach(([key, value]) => {
                const element = document.getElementById(key);
                if (element) {
                    element.textContent = value ? formatNumber(value) : '$0.00';
                }
            });
            
            // Update metadata
            const metadata = data.metadata;
            document.getElementById('eth_volume').textContent = 
                formatNumber(metadata.eth_24h_volume);
            document.getElementById('eth_change').innerHTML = 
                formatPercentage(metadata.eth_24h_change);
            document.getElementById('tvl-change').innerHTML = 
                `24h Change: ${formatPercentage(metadata.tvl_24h_change)}`;
            document.getElementById('revenue-change').innerHTML = 
                `24h Change: ${formatPercentage(metadata.fees_24h_change)}`;
            document.getElementById('stablecoins-change').innerHTML = 
                `24h Change: ${formatPercentage(metadata.stablecoins_24h_change)}`;
            
            // Update chart
            updateChart(data.gdp);
            
            // Update pie chart
            if (gdpPieChart) {
                updateGDPPieChart(data.components);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.querySelectorAll('.text-eth-blue').forEach(element => {
                if (element.textContent === 'Loading...') {
                    element.textContent = 'Error loading data';
                }
            });
        });
}

function formatPercentage(num) {
    const sign = num >= 0 ? '+' : '';
    const value = `${sign}${num.toFixed(2)}%`;
    if (Math.abs(num) < 0.005) {
        return `<span class="text-gray-400">${value}</span>`;
    } else if (num > 0) {
        return `<span class="text-green-400">${value}</span>`;
    } else if (num < 0) {
        return `<span class="text-red-400">${value}</span>`;
    }
    return `<span class="text-gray-400">${value}</span>`;
}

function updateChart(gdpValue) {
    if (gdpChart) {
        if (!CONFIG.enableTimeline) {
            // If timeline is disabled, just show the current value without a chart
            gdpChart.data.labels = [];
            gdpChart.data.datasets[0].data = [gdpValue];
            gdpChart.options.scales.x.display = false;  // Hide x-axis
            gdpChart.options.scales.y.display = false;  // Hide y-axis
            gdpChart.options.plugins.tooltip.enabled = false;  // Disable tooltips
        } else {
            const now = new Date();
            gdpChart.data.labels.push(now.toLocaleTimeString());
            gdpChart.data.datasets[0].data.push(gdpValue);
            
            // Keep only last 24 points
            if (gdpChart.data.labels.length > 24) {
                gdpChart.data.labels.shift();
                gdpChart.data.datasets[0].data.shift();
            }
        }
        gdpChart.update();
    }
}

// Add this after your existing chart code

let gdpPieChart = null;

function initializePieChart() {
    const ctx = document.getElementById('gdp-pie-chart').getContext('2d');
    gdpPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                'Monetary Base',
                'DeFi TVL',
                'Protocol Revenue',
                'Stablecoins',
                'Protocol Market Caps',
                'Cultural Capital'
            ],
            datasets: [{
                data: [0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    '#627EEA',  // Ethereum Blue
                    '#FF007A',  // Uniswap Pink
                    '#2172E5',  // Aave Blue
                    '#00ED76',  // USDC Green
                    '#8C8C8C',  // Gray
                    '#FFB23F'   // Orange
                ],
                borderWidth: 0,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    align: 'center',
                    labels: {
                        color: '#fff',
                        font: {
                            family: 'Inter',
                            size: 14,
                            weight: '500'
                        },
                        padding: 25,
                        boxWidth: 15,
                        boxHeight: 15,
                        borderRadius: 4,
                        textAlign: 'left',
                        usePointStyle: true,
                        pointStyle: 'circle',
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const total = data.datasets[0].data.reduce((acc, val) => acc + val, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label} ${formatNumber(value)} (${percentage}%)`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        color: '#fff',
                                        fontColor: '#fff',
                                        strokeStyle: '#fff',
                                        lineWidth: 0,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initializeStablecoinsChart() {
    console.log('Initializing stablecoins chart...');
    const canvas = document.getElementById('stablecoins-distribution-chart');
    const debugInfo = document.getElementById('stablecoins-debug');
    
    if (!canvas) {
        console.error('Stablecoins canvas element not found');
        if (debugInfo) debugInfo.textContent = 'Error: Canvas element not found';
        return;
    }

    try {
        stablecoinsDistributionChart = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['USDT', 'USDC', 'DAI', 'Others'],
                datasets: [{
                    data: [40, 30, 20, 10],
                    backgroundColor: ['#26A17B', '#2775CA', '#F5AC37', '#8C8C8C']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            color: '#fff',
                            font: {
                                size: 10
                            }
                        }
                    }
                }
            }
        });
        
        if (debugInfo) debugInfo.textContent = 'Stablecoins chart initialized';
    } catch (error) {
        console.error('Error initializing stablecoins chart:', error);
        if (debugInfo) debugInfo.textContent = `Error: ${error.message}`;
    }
}

function initializeTestChart() {
    console.log('Initializing test chart...');
    const canvas = document.getElementById('test-chart');
    const debugInfo = document.getElementById('test-debug');
    
    if (!canvas) {
        console.error('Test canvas element not found');
        if (debugInfo) debugInfo.textContent = 'Error: Canvas element not found';
        return;
    }

    try {
        testChart = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Red', 'Blue', 'Yellow'],
                datasets: [{
                    data: [300, 200, 100],
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff'
                        }
                    }
                }
            }
        });
        
        if (debugInfo) debugInfo.textContent = 'Test chart initialized';
    } catch (error) {
        console.error('Error initializing test chart:', error);
        if (debugInfo) debugInfo.textContent = `Error: ${error.message}`;
    }
}

function sortData(data, column, direction) {
    return [...data].sort((a, b) => {
        let aValue = column === 'tvl' ? a[column] : 
                     column === 'change_1d' ? parseFloat(a[column]) :
                     column === 'apy' ? parseFloat(a[column]) : 
                     a[column].toString().toLowerCase();
        let bValue = column === 'tvl' ? b[column] : 
                     column === 'change_1d' ? parseFloat(b[column]) :
                     column === 'apy' ? parseFloat(b[column]) : 
                     b[column].toString().toLowerCase();
        
        if (direction === 'asc') {
            return aValue > bValue ? 1 : -1;
        }
        return aValue < bValue ? 1 : -1;
    });
}

function loadProtocolsData() {
    fetch('/api/protocols')
        .then(response => response.json())
        .then(data => {
            const sortedData = sortData(data, protocolSortConfig.column, protocolSortConfig.direction);
            const table = document.getElementById('topProtocolsTable');
            let html = `
                <table class="min-w-full divide-y divide-gray-700">
                    <thead>
                        <tr class="text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateProtocolSort('name')">
                                Protocol ${protocolSortConfig.column === 'name' ? (protocolSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateProtocolSort('category')">
                                Category ${protocolSortConfig.column === 'category' ? (protocolSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                            <th class="px-6 py-3 text-right cursor-pointer hover:bg-gray-700/50" onclick="updateProtocolSort('tvl')">
                                TVL ${protocolSortConfig.column === 'tvl' ? (protocolSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateProtocolSort('change_1d')">
                                24h Change ${protocolSortConfig.column === 'change_1d' ? (protocolSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-700 text-gray-300">
            `;
            
            sortedData.forEach(protocol => {
                html += `
                    <tr class="hover:bg-gray-700/50">
                        <td class="px-6 py-4">${protocol.name}</td>
                        <td class="px-6 py-4">${protocol.category}</td>
                        <td class="px-6 py-4 text-right">${formatNumber(protocol.tvl)}</td>
                        <td class="px-6 py-4 whitespace-nowrap ${protocol.change_1d >= 0 ? 'text-green-400' : 'text-red-400'}">
                            ${protocol.change_1d.toFixed(2)}%
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            table.innerHTML = html;
        });
}

function loadCategoryData() {
    fetch('/api/categories')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Raw category data:', data);
            
            if (!data || Object.keys(data).length === 0) {
                throw new Error('No category data received');
            }

            // Sort categories by TVL
            const sortedEntries = Object.entries(data).sort((a, b) => b[1] - a[1]);
            const labels = sortedEntries.map(([category]) => category);
            const values = sortedEntries.map(([, value]) => value);

            const chartData = {
                labels: labels,
                datasets: [{
                    data: values,
                    borderWidth: 2,
                    borderColor: '#1a1f2d',
                    hoverBorderWidth: 0,
                    hoverOffset: 20,
                    backgroundColor: [
                        'rgba(98, 126, 234, 0.9)',    // Ethereum Blue
                        'rgba(255, 0, 122, 0.9)',     // Uniswap Pink
                        'rgba(33, 114, 229, 0.9)',    // Aave Blue
                        'rgba(0, 237, 118, 0.9)',     // Green
                        'rgba(255, 178, 63, 0.9)',    // Orange
                        'rgba(140, 140, 140, 0.9)',   // Gray
                        ...generateColors(Math.max(0, labels.length - 6))
                    ],
                    hoverBackgroundColor: [
                        'rgba(98, 126, 234, 1)',
                        'rgba(255, 0, 122, 1)',
                        'rgba(33, 114, 229, 1)',
                        'rgba(0, 237, 118, 1)',
                        'rgba(255, 178, 63, 1)',
                        'rgba(140, 140, 140, 1)',
                        ...generateColors(Math.max(0, labels.length - 6)).map(color => color.replace('0.9', '1'))
                    ]
                }]
            };

            const ctx = document.getElementById('categoryChart');
            if (!ctx) {
                throw new Error('Canvas element not found');
            }

            // Clear the container and create a new canvas
            const container = ctx.parentElement;
            container.innerHTML = '';
            const newCanvas = document.createElement('canvas');
            newCanvas.id = 'categoryChart';
            container.appendChild(newCanvas);

            new Chart(newCanvas, {
                type: 'pie',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '5%',
                    animation: {
                        animateScale: true,
                        animateRotate: true,
                        duration: 2000,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true,
                        animationDuration: 200
                    },
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    family: 'Inter',
                                    size: 12,
                                    weight: '500'
                                },
                                usePointStyle: true,
                                pointStyle: 'circle',
                                boxWidth: 10,
                                padding: 25
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(17, 25, 40, 0.95)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            padding: 12,
                            cornerRadius: 8,
                            displayColors: true,
                            usePointStyle: true,
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            callbacks: {
                                title: function(tooltipItems) {
                                    return tooltipItems[0].label;
                                },
                                label: function(context) {
                                    const value = context.raw;
                                    const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return [
                                        `TVL: ${formatNumber(value)}`,
                                        `Share: ${percentage}%`
                                    ];
                                }
                            }
                        },
                        datalabels: {
                            color: '#fff',
                            textAlign: 'center',
                            font: {
                                family: 'Inter',
                                weight: 'bold'
                            },
                            formatter: function(value, context) {
                                const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return percentage + '%';
                            },
                            display: function(context) {
                                return context.dataset.data[context.dataIndex] / 
                                    context.dataset.data.reduce((a, b) => a + b) > 0.05;
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading category data:', error.message);
            const container = document.getElementById('categoryChart').parentElement;
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full">
                    <p class="text-center text-gray-400">Failed to load category data</p>
                    <p class="text-center text-gray-500 text-sm mt-2">${error.message}</p>
                </div>
            `;
        });
}

function loadYieldsData() {
    fetch('/api/yields')
        .then(response => response.json())
        .then(data => {
            const sortedData = sortData(data, yieldSortConfig.column, yieldSortConfig.direction);
            const table = document.getElementById('yieldsTable');
            let html = `
                <table class="min-w-full divide-y divide-gray-700">
                    <thead>
                        <tr class="text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateYieldSort('pool')">
                                Pool ${yieldSortConfig.column === 'pool' ? (yieldSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateYieldSort('protocol')">
                                Protocol ${yieldSortConfig.column === 'protocol' ? (yieldSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateYieldSort('apy')">
                                APY ${yieldSortConfig.column === 'apy' ? (yieldSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                            <th class="px-6 py-3 cursor-pointer hover:bg-gray-700/50" onclick="updateYieldSort('tvl')">
                                TVL ${yieldSortConfig.column === 'tvl' ? (yieldSortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-700 text-gray-300">
            `;
            
            sortedData.forEach(pool => {
                html += `
                    <tr class="hover:bg-gray-700/50 transition-colors duration-150 cursor-pointer"
                        onclick="window.open('https://defillama.com/yields?token=${pool.pool}', '_blank')">
                        <td class="px-6 py-4 whitespace-nowrap">${pool.pool}</td>
                        <td class="px-6 py-4 whitespace-nowrap">${pool.protocol}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-green-400">${pool.apy.toFixed(2)}%</td>
                        <td class="px-6 py-4 whitespace-nowrap">${formatNumber(pool.tvl)}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            table.innerHTML = html;
        });
}

// Helper function to generate colors for the pie chart
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(`hsl(${(i * 360) / count}, 70%, 50%)`);
    }
    return colors;
}

// Initialize chart and start updates
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    initializePieChart();
    initializeStablecoinsChart();
    initializeTestChart();
    if (CONFIG.enableTimeline) {
        initializeTimelineChart();
    }
    updateGDP();
    setInterval(updateGDP, 300000); // Update every 5 minutes
    
    // Wait a brief moment to ensure DOM is fully ready
    setTimeout(() => {
        loadProtocolsData();
        loadCategoryData();
        loadYieldsData();
        
        // Refresh data every 5 minutes
        setInterval(() => {
            loadProtocolsData();
            loadCategoryData();
            loadYieldsData();
        }, 300000);
    }, 100);
});

// Timeline-related code (commented out for now)
/*
function initializeTimelineChart() {
    // Timeline initialization code here
}

function fetchTimelineData(period) {
    // Timeline data fetching code here
}
*/

// Sorting update functions
function updateProtocolSort(column) {
    if (protocolSortConfig.column === column) {
        protocolSortConfig.direction = protocolSortConfig.direction === 'asc' ? 'desc' : 'asc';
    } else {
        protocolSortConfig.column = column;
        protocolSortConfig.direction = 'desc';
    }
    loadProtocolsData();
}

function updateYieldSort(column) {
    if (yieldSortConfig.column === column) {
        yieldSortConfig.direction = yieldSortConfig.direction === 'asc' ? 'desc' : 'asc';
    } else {
        yieldSortConfig.column = column;
        yieldSortConfig.direction = 'desc';
    }
    loadYieldsData();
}

function updateGDPPieChart(components) {
    const labels = [
        'Monetary Base',
        'DeFi TVL',
        'Protocol Revenue',
        'Stablecoins',
        'Protocol Market Caps'
    ];
    const values = [
        components.monetary_base,
        components.tvl,
        components.fees,
        components.stablecoins,
        components.protocols
    ];
    
    gdpPieChart.data.datasets[0].data = values;
    gdpPieChart.update();
}