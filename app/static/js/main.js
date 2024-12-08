// Feature flags
const CONFIG = {
    enableTimeline: false  // Set to true to enable timeline feature
};

// Chart configuration
let gdpChart = null;

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
            
            // Update chart
            updateChart(data.gdp);
            
            // Update pie chart
            if (gdpPieChart) {
                // Create array of objects with labels and values
                const components = [
                    { label: 'Monetary Base', value: data.components.monetary_base },
                    { label: 'DeFi TVL', value: data.components.tvl },
                    { label: 'Protocol Revenue', value: data.components.fees },
                    { label: 'Stablecoins', value: data.components.stablecoins },
                    { label: 'Protocol Market Caps', value: data.components.protocols },
                    { label: 'Cultural Capital', value: data.components.cultural || 0 }
                ];
                
                // Sort components by value in descending order
                components.sort((a, b) => b.value - a.value);
                
                // Update chart data
                gdpPieChart.data.labels = components.map(c => c.label);
                gdpPieChart.data.datasets[0].data = components.map(c => c.value);
                
                // Reorder colors to match sorted data
                const colorMap = {
                    'Monetary Base': '#627EEA',
                    'DeFi TVL': '#FF007A',
                    'Protocol Revenue': '#2172E5',
                    'Stablecoins': '#00ED76',
                    'Protocol Market Caps': '#8C8C8C',
                    'Cultural Capital': '#FFB23F'
                };
                gdpPieChart.data.datasets[0].backgroundColor = components.map(c => colorMap[c.label]);
                
                gdpPieChart.update();
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

// Initialize chart and start updates
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    initializePieChart();
    if (CONFIG.enableTimeline) {
        initializeTimelineChart();
    }
    updateGDP();
    setInterval(updateGDP, 300000); // Update every 5 minutes
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