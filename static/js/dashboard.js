console.log("Dashboard.js er lastet!");

// Håndter transport-type knapper
document.querySelectorAll('.transport-btn').forEach(button => {
    button.addEventListener('click', function() {
        // Fjern active class fra alle knapper
        document.querySelectorAll('.transport-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        // Legg til active class på den klikkede knappen
        this.classList.add('active');
        
        // Hent data for valgt transporttype
        const transportType = this.dataset.type;
        updateStats(transportType);
    });
});

function updateStats(transportType = 'all') {
    console.log(`Henter statistikk for ${transportType}`);
    fetch(`/api/stats?transport_type=${transportType}`)
        .then(response => response.json())
        .then(data => {
            console.log("Mottatt statistikk:", data);
            
            // Oppdater sanntids-statistikk
            document.getElementById('totalTrips').textContent = 
                data.summary.total_trips;
            document.getElementById('avgDelay').textContent = 
                data.summary.avg_delay.toFixed(1);
            document.getElementById('punctuality').textContent = 
                data.summary.punctuality.toFixed(1);
            
            // Oppdater transportfordeling
            updateTransportDistribution(data.transport_distribution);
            
            // Oppdater andre deler av dashbordet
            updateTopDelays(data.top_delays);
            updateDelayDistribution(data.delay_distribution);
        })
        .catch(error => {
            console.error('Feil ved oppdatering av statistikk:', error);
        });
}

function updateWeeklyStats() {
    console.log("Henter ukentlig statistikk...");
    fetch('/weekly_stats')
        .then(response => response.json())
        .then(data => {
            console.log("Mottatt ukentlig statistikk:", data);
            
            if (data.error) {
                console.error("Feil fra server:", data.error);
                return;
            }
            
            // Oppdater statistikk
            document.getElementById('weeklyPunctuality').textContent = 
                `${data.punctuality || 0}%`;
            document.getElementById('weeklyAvgDelay').textContent = 
                `${data.avg_delay || 0} min`;
            
            // Konverter datoer til ukedager
            const dates = data.dates.map(formatNorwegianDate);
            
            // Oppdater grafen
            const ctx = document.getElementById('weeklyDelayChart');
            if (!ctx) {
                console.error("Fant ikke canvas element");
                return;
            }
            
            if (window.weeklyChart) {
                window.weeklyChart.destroy();
            }
            
            window.weeklyChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Forsinkelser (minutter)',
                        data: data.total_minutes,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                autoSkip: false,
                                maxRotation: 0,
                                minRotation: 0
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Feil ved henting av ukentlig statistikk:", error);
        });
}

function updateTotalStats() {
    console.log("Henter total statistikk...");
    fetch('/total_stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalDelay').textContent = 
                formatDuration(data.total_minutes);
            document.getElementById('busDelay').textContent = 
                formatDuration(data.bus_minutes);
            document.getElementById('trainDelay').textContent = 
                formatDuration(data.train_minutes);
            document.getElementById('tramDelay').textContent = 
                formatDuration(data.tram_minutes);
        })
        .catch(error => console.error("Feil ved henting av total statistikk:", error));
}

function formatDuration(minutes) {
    if (minutes < 60) {
        return `${minutes} minutter`;
    } else if (minutes < 1440) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours} timer${mins > 0 ? ` og ${mins} minutter` : ''}`;
    } else {
        const days = Math.floor(minutes / 1440);
        const hours = Math.floor((minutes % 1440) / 60);
        return `${days} dager${hours > 0 ? ` og ${hours} timer` : ''}`;
    }
}

function updateSummaryStats(summary) {
    if (!summary) return;
    
    document.getElementById('totalTrips').textContent = summary.total_trips || '0';
    document.getElementById('avgDelay').textContent = summary.avg_delay?.toFixed(1) || '0';
    document.getElementById('punctuality').textContent = summary.punctuality?.toFixed(1) || '0';
}

function updateTopDelays(delays) {
    if (!delays) return;
    
    const tbody = document.querySelector('#topDelays tbody');
    tbody.innerHTML = ''; // Tøm eksisterende innhold
    
    delays.forEach(delay => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${delay.line}</td>
            <td>${delay.type}</td>
            <td>${delay.station}</td>
            <td>${delay.delay} min</td>
        `;
        tbody.appendChild(row);
    });
}

function updateTransportDistribution(distribution) {
    if (!distribution) return;
    
    // Oppdater prosentene direkte fra transport_distribution objektet
    document.getElementById('railPercentage').textContent = 
        distribution.rail.percentage.toFixed(1);
    document.getElementById('busPercentage').textContent = 
        distribution.bus.percentage.toFixed(1);
    document.getElementById('tramPercentage').textContent = 
        distribution.tram.percentage.toFixed(1);
    
    console.log('Transportfordeling oppdatert:', distribution);
}

function updateDelayDistribution(distribution) {
    if (!distribution) return;
    
    const ctx = document.getElementById('delayDistChart');
    if (!ctx) return;
    
    const chartData = {
        labels: ['0-5', '5-10', '10-15', '15-30', '30+'],
        datasets: [{
            label: 'Forsinkelser (%)',
            data: [
                distribution['0-5'] || 0,
                distribution['5-10'] || 0,
                distribution['10-15'] || 0,
                distribution['15-30'] || 0,
                distribution['30+'] || 0
            ],
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    };

    if (window.delayDistChart) {
        window.delayDistChart.destroy();
    }
    
    window.delayDistChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `${value}%`
                    }
                }
            }
        }
    });
}

function updateOperatorStats(stats) {
    if (!stats) return;
    
    const container = document.getElementById('operator-stats');
    container.innerHTML = ''; // Tøm eksisterende innhold
    
    stats.forEach(operator => {
        const operatorDiv = document.createElement('div');
        operatorDiv.className = 'operator-stat';
        operatorDiv.innerHTML = `
            <div class="operator-name">${operator.name}</div>
            <div class="operator-values">
                <div class="operator-value">
                    <span class="value-label">Punktlighet:</span>
                    <span class="value-number">${operator.punctuality.toFixed(1)}%</span>
                </div>
                <div class="operator-value">
                    <span class="value-label">Snitt forsinkelse:</span>
                    <span class="value-number">${operator.avg_delay.toFixed(1)} min</span>
                </div>
            </div>
        `;
        container.appendChild(operatorDiv);
    });
}

function formatNorwegianDate(dateStr) {
    try {
        // Sjekk om dateStr er gyldig
        if (!dateStr || typeof dateStr !== 'string') {
            console.error('Ugyldig datostreng:', dateStr);
            return dateStr;
        }

        // Håndter både "DD.MM" og "YYYY-MM-DD" format
        let day, month;
        if (dateStr.includes('.')) {
            [day, month] = dateStr.split('.');
        } else if (dateStr.includes('-')) {
            const parts = dateStr.split('-');
            month = parts[1];
            day = parts[2];
        } else {
            console.error('Ukjent datoformat:', dateStr);
            return dateStr;
        }

        // Lag en dato-streng med ISO format
        const dateObj = new Date(2025, parseInt(month) - 1, parseInt(day));
        
        // Verifiser at datoen er gyldig
        if (isNaN(dateObj.getTime())) {
            console.error('Ugyldig dato:', dateStr);
            return dateStr;
        }

        // Hent ukedag på norsk (full navn)
        const weekdays = ['Søndag', 'Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag'];
        const weekday = weekdays[dateObj.getDay()];
        
        // Formater datoen som "DD.MM" og returner med ukedag først
        const formattedDate = `${day.padStart(2, '0')}.${month.padStart(2, '0')}`;
        return `${weekday}\n${formattedDate}`;
    } catch (e) {
        console.error("Feil ved datoformatering:", e, dateStr);
        return dateStr;
    }
}

// Start oppdateringer når siden lastes
document.addEventListener('DOMContentLoaded', () => {
    console.log("Starter statistikk-oppdateringer...");
    updateStats('all');
    updateWeeklyStats();
    updateTotalStats();
    
    // Oppdater hvert 30. sekund
    setInterval(() => {
        const activeTransportType = document.querySelector('.transport-btn.active').dataset.type;
        updateStats(activeTransportType);
        updateWeeklyStats();
        updateTotalStats();
    }, 30000);
}); 