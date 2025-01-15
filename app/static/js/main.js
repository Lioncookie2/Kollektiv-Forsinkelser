let currentTransportType = 'all';
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    setupTransportButtons();
    setupCharts();
    updateDashboard();
    setInterval(updateDashboard, 60000); // Oppdater hvert minutt
});

function setupTransportButtons() {
    document.querySelectorAll('.transport-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.transport-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTransportType = btn.dataset.type;
            updateTransportTitle();
            updateDashboard();
        });
    });
}

function setupCharts() {
    // Dagens statistikk
    charts.today = new Chart(document.getElementById('todayChart'), {
        type: 'line',
        data: {
            labels: Array.from({length: 24}, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Forsinkelser',
                data: Array(24).fill(0),
                borderColor: '#2c3e50',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Transport type fordeling
    charts.transportTypes = new Chart(document.getElementById('transportTypeChart'), {
        type: 'doughnut',
        data: {
            labels: ['Tog', 'Buss', 'Trikk'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#2c3e50', '#3498db', '#e74c3c']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Forsinkelsesfordeling
    charts.delayDist = new Chart(document.getElementById('delayDistChart'), {
        type: 'bar',
        data: {
            labels: ['0-5', '5-10', '10-15', '15-30', '30+'],
            datasets: [{
                label: 'Antall avganger',
                data: [0, 0, 0, 0, 0],
                backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateDashboard() {
    console.log('Henter oppdatert statistikk...');
    fetch(`/api/stats?transport_type=${currentTransportType}`)
        .then(response => response.json())
        .then(data => {
            console.log('Mottatt data:', data);
            updateSummary(data.summary);
            updateCharts(data);
            updateOperatorStats(data.details.by_operator);
        })
        .catch(error => console.error('Feil ved henting av statistikk:', error));
}

function updateSummary(summary) {
    document.getElementById('total-punctuality').textContent = `${summary.punctuality || 0}%`;
    document.getElementById('total-delay').textContent = `${summary.avg_delay || 0} min`;
    document.getElementById('total-trips').textContent = summary.total_trips || 0;
}

function updateCharts(data) {
    // Oppdater dagens statistikk
    if (data.today_delays) {
        charts.today.data.datasets[0].data = data.today_delays;
        charts.today.update();
    }

    // Oppdater transporttype-fordeling
    if (data.details && data.details.by_type) {
        const typeData = data.details.by_type;
        charts.transportTypes.data.datasets[0].data = [
            typeData.rail?.total_trips || 0,
            typeData.bus?.total_trips || 0,
            typeData.tram?.total_trips || 0
        ];
        charts.transportTypes.update();
    }

    // Oppdater forsinkelsesfordeling
    if (data.delay_distribution) {
        charts.delayDist.data.datasets[0].data = data.delay_distribution;
        charts.delayDist.update();
    }
}

function updateOperatorStats(operatorData) {
    const container = document.getElementById('operator-stats');
    if (!container) return;

    container.innerHTML = '';
    if (!operatorData) return;

    Object.entries(operatorData).forEach(([operator, stats]) => {
        const card = document.createElement('div');
        card.className = 'operator-card';
        card.innerHTML = `
            <h4>${operator}</h4>
            <p>Punktlighet: ${stats.punctuality || 0}%</p>
            <p>Snitt forsinkelse: ${stats.avg_delay || 0} min</p>
            <p>Antall avganger: ${stats.total_trips || 0}</p>
        `;
        container.appendChild(card);
    });
}

function updateTransportTitle() {
    const titles = {
        'all': 'Alle transportmidler',
        'rail': 'Tog',
        'bus': 'Buss',
        'tram': 'Trikk'
    };
    const titleElement = document.getElementById('transport-title');
    if (titleElement) {
        titleElement.textContent = ` - ${titles[currentTransportType] || ''}`;
    }
} 