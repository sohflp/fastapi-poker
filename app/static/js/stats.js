const ctx = document.getElementById('pokerChart');

new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        responsive: true,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            title: {
                display: true,
                text: 'Players performance over time',
                color: 'white',
                font: {
                    size: 20,
                    weight: 'bold'
                }
            },
            legend: {
                position: 'right', // or 'left'
                labels: {
                    boxWidth: 12,
                    padding: 10,
                    color: 'white'
                }
            }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'week'
                },
                title: {
                    display: false
                },
                ticks: {
                    color: 'white'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Points',
                    color: 'white',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                beginAtZero: true,
                ticks: {
                    color: 'white'
                }
            }
        }
    }
});