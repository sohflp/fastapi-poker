const options = {
  chart: {
    type: 'line',
    height: 600,
    background: "rgba(0,0,0,0.65)",
    toolbar: {
      show: false
    },
    zoom: {
      enabled: false
    }
  },

  series: series,

  stroke: {
    width: window.innerWidth < 768 ? 1 : 2,
    curve: 'smooth',
    width: 2
  },

  xaxis: {
    type: 'datetime',
    categories: categories,
    labels: {
      style: {
        colors: '#ffffff'
      }
    }
  },

  yaxis: {
    min: 0,
    title: {
      text: 'Points',
      style: {
        color: '#ffffff',
        fontSize: '16px',
        fontWeight: 600
      }
    },
    labels: {
      style: {
        colors: '#ffffff'
      }
    }
  },

  legend: {
    position: 'right',
    labels: {
      colors: '#ffffff'
    }
  },

  title: {
    style: {
      color: '#ffffff',
      fontSize: '20px',
      fontWeight: 'bold'
    }
  },

  tooltip: {
    shared: true,
    intersect: false
  },

  grid: {
    borderColor: '#444',
    padding: {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20
    }
  },

  theme: {
    mode: 'dark'
  },

  responsive: [
    {
      breakpoint: 768,
      options: {
        legend: {
          position: 'bottom'
        },
        chart: {
          height: 400
        }
      }
    }
  ]
};

const chart = new ApexCharts(document.querySelector("#pokerChart"), options);
chart.render();