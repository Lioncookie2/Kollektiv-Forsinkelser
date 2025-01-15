<<<<<<< HEAD
document.addEventListener('DOMContentLoaded', function() {
    let selectedType = 'all';
    let weeklyChart = null;
    let delayDistChart = null;

    // Funksjon for å oppdatere data
    function updateData() {
        const selectedType = document.querySelector('.transport-btn.active').dataset.type;
        console.log('Fetching data for transport type:', selectedType);
        
        // Hent total statistikk
        fetch(`/total_stats?transport_type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                console.log('Total stats:', data);
                document.getElementById('totalTrips').textContent = data.total_trips;
                document.getElementById('avgDelay').textContent = data.avg_delay.toFixed(1);
                document.getElementById('punctuality').textContent = data.punctuality.toFixed(1);
            })
            .catch(error => console.error('Error fetching total stats:', error));

        // Hent transporttype-spesifikk statistikk
        fetch(`/api/stats?transport_type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                console.log('Transport stats:', data);
                updateDelayStats(data);
            })
            .catch(error => console.error('Error fetching transport stats:', error));

        // Hent operatørstatistikk
        fetch(`/operator_stats?transport_type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                updateOperatorStats(data);
            })
            .catch(error => console.error('Error fetching operator stats:', error));

        // Hent ukentlig statistikk
        fetch(`/weekly_stats?transport_type=${selectedType}`)
            .then(response => response.json())
            .then(response => {
                console.log('Weekly stats data:', response);
                if (response.data && response.data.length > 0) {
                    updateWeeklyChart(response.data);
                }
            })
            .catch(error => console.error('Error:', error));

        // Hent forsinkelsesfordeling
        fetch(`/delay_distribution?transport_type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                console.log('Delay distribution data:', data);
                if (Object.keys(data).length > 0) {
                    updateDelayDistribution(data);
                }
            })
            .catch(error => console.error('Error:', error));

        // Hent total ventetid
        fetch('/total_waiting_time')
            .then(response => response.json())
            .then(data => {
                updateTotalWaitingTime(data);
            })
            .catch(error => console.error('Error fetching total waiting time:', error));

        // Hent største forsinkelser med valgt transporttype
        fetch(`/top_delays?transport_type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                updateTopDelays(data);
            })
            .catch(error => console.error('Error fetching top delays:', error));

        // Hent linjestatistikk
        fetch(`/line_stats?transport_type=${selectedType}`)
            .then(response => {
                console.log('Line stats response:', response);
                return response.json();
            })
            .then(data => {
                console.log('Line stats data received:', data);
                updateLineStats(data);
            })
            .catch(error => {
                console.error('Error fetching line stats:', error);
                // Vis feilmelding i grensesnittet
                const container = document.querySelector('.operator-stats');
                container.innerHTML = `
                    <div class="error-message">
                        Kunne ikke hente linjestatistikk. Prøv igjen senere.
                    </div>
                `;
            });

        // Oppdater transportfordeling
        updateTransportDistribution();
    }

    // Oppdater transport-knapper
    document.querySelectorAll('.transport-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.transport-btn').forEach(btn => 
                btn.classList.remove('active'));
            this.classList.add('active');
            selectedType = this.dataset.type;
            updateData();
        });
    });

    // Initial update
    updateData();

    // Update every minute
    setInterval(updateData, 60000);
});

function updateDelayStats(delays) {
    // Beregn statistikk basert på forsinkelsesdata
    let totalDelays = delays.length;
    let avgDelay = delays.reduce((sum, d) => sum + d.delay_minutes, 0) / totalDelays || 0;
    
    // Oppdater UI
    document.getElementById('totalTrips').textContent = totalDelays;
    document.getElementById('avgDelay').textContent = avgDelay.toFixed(1);
    
    // Beregn transporttype-fordeling
    let types = {
        'rail': 0,
        'bus': 0,
        'tram': 0
    };
    
    delays.forEach(d => {
        if (d.transport_type === 'rail') types.rail++;
        if (d.transport_type === 'bus') types.bus++;
        if (d.transport_type === 'tram') types.tram++;
    });
    
    // Oppdater prosentandeler
    let total = Object.values(types).reduce((a, b) => a + b, 0);
    if (total > 0) {
        document.getElementById('railPercentage').textContent = 
            ((types.rail / total) * 100).toFixed(1);
        document.getElementById('busPercentage').textContent = 
            ((types.bus / total) * 100).toFixed(1);
        document.getElementById('tramPercentage').textContent = 
            ((types.tram / total) * 100).toFixed(1);
=======
﻿document.addEventListener('DOMContentLoaded', function() {
    let currentTransportType = 'all';
    let weeklyChart = null;

    // Initialize transport type buttons
    document.querySelectorAll('.transport-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.transport-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTransportType = btn.dataset.type;
            updateData();
        });
    });

    function updateData() {
        // Update delays
        fetch(/api/stats?transport_type=)
            .then(response => response.json())
            .then(data => {
                updateDelaysList(data);
            });

        // Update total stats
        fetch('/total_stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-delays').textContent = data.total_delays;
                document.getElementById('avg-delay').textContent = ${data.avg_delay} min;
            });

        // Update weekly stats
        fetch('/weekly_stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('punctuality').textContent = ${data.punctuality}%;
                updateWeeklyChart(data);
            });
    }

    function updateDelaysList(delays) {
        const container = document.getElementById('delays-list');
        container.innerHTML = '';

        if (delays.length === 0) {
            container.innerHTML = '<p>Ingen aktive forsinkelser</p>';
            return;
        }

        delays.forEach(delay => {
            const delayElement = document.createElement('div');
            delayElement.className = 'delay-item';
            delayElement.innerHTML = 
                <p><strong></strong> - </p>
                <p>Forsinkelse:  minutter</p>
            ;
            container.appendChild(delayElement);
        });
>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    }

<<<<<<< HEAD
function updateWeeklyChart(data) {
    console.log('Updating weekly chart with data:', data);
    const ctx = document.getElementById('weeklyDelayChart').getContext('2d');
    
    if (window.weeklyDelayChart instanceof Chart) {
        window.weeklyDelayChart.destroy();
    }
    
    // Finn maksverdi for y-aksen
    const maxValue = Math.max(...data.map(d => d.count));
    const yMax = Math.ceil(maxValue * 1.2);  // Legg til 20% margin på toppen
    
    window.weeklyDelayChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => `${d.weekday}\n${d.date}`),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                barThickness: 30
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: yMax,
                    ticks: {
                        stepSize: Math.ceil(yMax / 5),
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });

    // Beregn totalt antall forsinkelser
    const totalDelays = data.reduce((sum, day) => sum + day.count, 0);
    
    // Finn verste dag
    const worstDay = data.reduce((worst, current) => 
        current.count > worst.count ? current : worst
    );
    
    // Oppdater statistikk
    document.querySelector('.total-delays').textContent = `${totalDelays} forsinkelser`;
    document.querySelector('.worst-day').textContent = `${worstDay.weekday} (${worstDay.count})`;
}

function updateDelayDistribution(data) {
    const ctx = document.getElementById('delayDistChart').getContext('2d');
    
    // Riktig måte å sjekke og ødelegge eksisterende chart
    if (window.delayDistChart instanceof Chart) {
        window.delayDistChart.destroy();
    }
    
    window.delayDistChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Antall forsinkelser',
                data: Object.values(data),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateTotalWaitingTime(data) {
    // Oppdater total ventetid
    document.getElementById('totalDelay').textContent = data.formatted_total;
    
    // Oppdater per transporttype (konverter til timer)
    document.getElementById('busDelay').textContent = 
        Math.round(data.bus / 60) + ' timer';
    document.getElementById('trainDelay').textContent = 
        Math.round(data.rail / 60) + ' timer';
    document.getElementById('tramDelay').textContent = 
        Math.round(data.tram / 60) + ' timer';
}

function updateTopDelays(delays) {
    const tbody = document.querySelector('#topDelays tbody');
    tbody.innerHTML = '';
    
    if (delays.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="4" class="no-delays">Ingen forsinkelser</td>
        `;
        tbody.appendChild(row);
        return;
    }
    
    delays.forEach(delay => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${delay.line}</td>
            <td>${getTransportIcon(delay.transport_type)}</td>
            <td>${delay.station}</td>
            <td>${delay.delay_minutes} min</td>
        `;
        tbody.appendChild(row);
    });
}

function getTransportIcon(type) {
    const icons = {
        'bus': '🚌',
        'rail': '🚂',
        'tram': '🚊'
    };
    return icons[type] || '🚌';
}

function updateOperatorStats(data) {
    const container = document.querySelector('.operator-stats');
    container.innerHTML = ''; // Tøm eksisterende innhold

    // Sorter operatører etter antall forsinkelser
    const sortedOperators = Object.entries(data)
        .sort(([,a], [,b]) => b.delays - a.delays);

    sortedOperators.forEach(([operator, stats]) => {
        const operatorDiv = document.createElement('div');
        operatorDiv.className = 'operator-item';
        
        const avgDelay = stats.total_delay_minutes / stats.delays;
        const punctuality = 100 - (stats.delays / stats.total_trips * 100);

        operatorDiv.innerHTML = `
            <div class="operator-header">
                <h4>${operator}</h4>
                <span class="operator-type">${stats.transport_type}</span>
            </div>
            <div class="operator-stats-grid">
                <div class="stat-item">
                    <span class="stat-value">${stats.delays}</span>
                    <span class="stat-label">Forsinkelser</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${avgDelay.toFixed(1)}</span>
                    <span class="stat-label">Snitt (min)</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${punctuality.toFixed(1)}%</span>
                    <span class="stat-label">Punktlighet</span>
                </div>
            </div>
        `;
        
        container.appendChild(operatorDiv);
    });
}

function updateLineStats(data) {
    console.log('Updating line stats with data:', data);
    
    const container = document.querySelector('.operator-stats');
    container.innerHTML = '<h3>Topp 5 mest forsinkede linjer (siste 24t)</h3>';

    const sortedLines = Object.entries(data)
        .sort(([,a], [,b]) => b.total_delay_minutes - a.total_delay_minutes);
    
    console.log('Sorted lines:', sortedLines);

    if (sortedLines.length === 0) {
        container.innerHTML += `
            <div class="no-data">
                Ingen forsinkelser funnet for valgt transporttype
            </div>
        `;
        return;
    }

    sortedLines.forEach(([line, stats]) => {
        console.log(`Creating element for line ${line}:`, stats);
        
        const lineDiv = document.createElement('div');
        lineDiv.className = 'operator-item';
        
        const transportIcon = {
            'bus': '🚌',
            'rail': '🚂',
            'tram': '🚊'
        }[stats.transport_type] || '🚌';

        lineDiv.innerHTML = `
            <div class="operator-header">
                <h4>${transportIcon} Linje ${line}</h4>
                <span class="operator-type">${stats.transport_type}</span>
            </div>
            <div class="operator-stats-grid">
                <div class="stat-item">
                    <span class="stat-value">${stats.delays} / ${stats.total_trips}</span>
                    <span class="stat-label">Andel forsinkelser</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${stats.avg_delay}</span>
                    <span class="stat-label">Snitt (min)</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${stats.total_delay_minutes}</span>
                    <span class="stat-label">Total (min)</span>
                </div>
            </div>
        `;
        
        container.appendChild(lineDiv);
    });
}

function updateTransportDistribution() {
    fetch('/transport_distribution')
        .then(response => response.json())
        .then(data => {
            // Oppdater prosentvisning med animasjon
            animateValue('railPercentage', data.rail);
            animateValue('busPercentage', data.bus);
            animateValue('tramPercentage', data.tram);
            
            // Oppdater bakgrunnsfarge basert på prosent
            updateTransportBackground('rail', data.rail);
            updateTransportBackground('bus', data.bus);
            updateTransportBackground('tram', data.tram);
        })
        .catch(error => console.error('Error:', error));
}

function animateValue(elementId, end) {
    const element = document.getElementById(elementId);
    const start = parseInt(element.textContent);
    const duration = 1000; // 1 sekund
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const value = Math.floor(start + (end - start) * progress);
        element.textContent = value;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function updateTransportBackground(type, percentage) {
    const container = document.querySelector(`.transport-type img[alt="${type === 'rail' ? 'Tog' : type === 'bus' ? 'Buss' : 'Trikk'}"]`)
        .closest('.transport-type');
    
    // Beregn opacity basert på prosent (0-100 blir til 0.1-1.0)
    const opacity = 0.1 + (percentage / 100) * 0.9;
    
    // Sett bakgrunnsfarge med variabel opacity
    container.style.backgroundColor = `rgba(var(--primary-rgb), ${opacity})`;
} 
=======
    function updateWeeklyChart(data) {
        const ctx = document.getElementById('weekly-chart').getContext('2d');
        
        if (weeklyChart) {
            weeklyChart.destroy();
        }

        weeklyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Antall forsinkelser',
                    data: data.delays,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Initial update
    updateData();

    // Update every minute
    setInterval(updateData, 60000);
});
>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
