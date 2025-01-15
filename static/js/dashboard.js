document.addEventListener('DOMContentLoaded', function() {
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
        fetch(`/api/stats?transport_type=${currentTransportType}`)
            .then(response => response.json())
            .then(data => {
                updateDelaysList(data);
            });

        // Update total stats
        fetch('/total_stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-delays').textContent = data.total_delays;
                document.getElementById('avg-delay').textContent = `${data.avg_delay} min`;
            });

        // Update weekly stats
        fetch('/weekly_stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('punctuality').textContent = `${data.punctuality}%`;
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
            delayElement.innerHTML = `
                <p><strong>${delay.line}</strong> - ${delay.station}</p>
                <p>Forsinkelse: ${delay.delay_minutes} minutter</p>
            `;
            container.appendChild(delayElement);
        });
    }

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