/**
 * Campus Energy Consumption Monitoring & Analytics Dashboard
 * Frontend Application & Chart.js Orchestration Script
 */

let charts = {};

// Color Palette Constants
const PALETTE = {
  emerald: '#10b981',
  emeraldDark: '#059669',
  emeraldLight: 'rgba(16, 185, 129, 0.15)',
  navy: '#1e293b',
  navyDark: '#0f172a',
  blue: '#0ea5e9',
  blueLight: 'rgba(14, 165, 233, 0.15)',
  amber: '#f59e0b',
  red: '#ef4444',
  purple: '#8b5cf6',
  gray: '#94a3b8',
  buildingColors: [
    '#10b981', '#0ea5e9', '#6366f1', '#f59e0b', '#ec4899', '#14b8a6', '#8b5cf6'
  ]
};

// Initialize Dashboard on Document Ready
document.addEventListener('DOMContentLoaded', () => {
  setupFilterListeners();
  setupDemoHandlers();
  setupDataManagementHandlers();

  // If on pages with charts, initialize them
  if (document.getElementById('chartBuildingConsumption')) {
    initOverviewCharts();
  }
  if (document.getElementById('chartTrendsDaily')) {
    initTrendsCharts();
  }
  if (document.getElementById('chartBuildingPeaks')) {
    initBuildingPageCharts();
  }
});

// Helper: Extract current filter parameters from DOM
function getFilterParams() {
  const params = new URLSearchParams();
  const b = document.getElementById('filterBuilding')?.value;
  const sDate = document.getElementById('filterStartDate')?.value;
  const eDate = document.getElementById('filterEndDate')?.value;
  const m = document.getElementById('filterMonth')?.value;
  const src = document.getElementById('filterSource')?.value;
  const dt = document.getElementById('filterDayType')?.value;

  if (b && b !== 'All') params.append('building', b);
  if (sDate) params.append('start_date', sDate);
  if (eDate) params.append('end_date', eDate);
  if (m && m !== 'All') params.append('month', m);
  if (src && src !== 'All') params.append('source', src);
  if (dt && dt !== 'All') params.append('day_type', dt);

  return params;
}

// Setup Event Listeners for Filters
function setupFilterListeners() {
  const filterInputs = [
    'filterBuilding', 'filterStartDate', 'filterEndDate',
    'filterMonth', 'filterSource', 'filterDayType'
  ];

  filterInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => {
        applyFilters();
      });
    }
  });

  const resetBtn = document.getElementById('btnResetFilters');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      filterInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          if (el.tagName === 'SELECT') el.value = 'All';
          if (el.tagName === 'INPUT') el.value = '';
        }
      });
      applyFilters();
    });
  }
}

// Trigger refresh across all components when filters change
function applyFilters() {
  const params = getFilterParams();

  // 1. Update KPI Cards
  updateKpiCards(params);

  // 2. Update Charts
  if (charts.buildingConsumption) updateBuildingChart(params);
  if (charts.dailyTrend) updateDailyTrendChart(params);
  if (charts.hourlyPattern) updateHourlyChart(params);
  if (charts.sourceDist) updateSourceChart(params);
  if (charts.occupancyScatter) updateOccupancyScatter(params);
  if (charts.monthlyTrend) updateMonthlyTrendChart(params);
  if (charts.buildingPeaks) updateBuildingPeaksChart(params);

  // 3. Update Anomalies List if on anomaly page
  if (document.getElementById('anomaliesTableBody')) {
    updateAnomaliesTable(params);
  }
}

// ==========================================================================
// KPI Cards Updater
// ==========================================================================

function updateKpiCards(params) {
  fetch(`/api/kpis?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      setKpiText('kpiTotalKwh', `${data.total_consumption_kwh.toLocaleString()} kWh`);
      setKpiText('kpiMwh', `(${data.total_consumption_mwh.toLocaleString()} MWh)`);
      setKpiText('kpiBuildings', data.buildings_monitored);
      setKpiText('kpiDailyAvg', `${data.avg_daily_consumption_kwh.toLocaleString()} kWh/day`);
      setKpiText('kpiPeakDemand', `${data.peak_demand_kw.toLocaleString()} kW`);
      setKpiText('kpiTotalRecords', data.total_records.toLocaleString());
      setKpiText('kpiAnomalies', data.anomalies_detected);
      setKpiText('kpiCo2', `${data.estimated_co2_tonnes.toLocaleString()} Tonnes CO2e`);
    })
    .catch(err => console.error('Error fetching KPIs:', err));
}

function setKpiText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

// ==========================================================================
// Chart.js Visualizations: Overview Dashboard
// ==========================================================================

function initOverviewCharts() {
  const params = getFilterParams();

  // A. Building-wise Energy Consumption (Bar Chart)
  fetch(`/api/charts/building-consumption?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartBuildingConsumption').getContext('2d');
      const bgColors = data.is_highest.map(isHigh => isHigh ? PALETTE.amber : PALETTE.emerald);

      charts.buildingConsumption = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Total Energy (kWh)',
            data: data.values,
            backgroundColor: bgColors,
            borderRadius: 6,
            borderSkipped: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.parsed.y.toLocaleString()} kWh (${data.percentages[ctx.dataIndex]}%)`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9' },
              ticks: { callback: v => `${(v/1000).toFixed(0)}k kWh` }
            },
            x: { grid: { display: false } }
          }
        }
      });
    });

  // B. Daily Energy Consumption (Line Chart)
  fetch(`/api/charts/daily-trend?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartDailyTrend').getContext('2d');
      charts.dailyTrend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.dates,
          datasets: [
            {
              label: 'Daily Consumption (kWh)',
              data: data.consumption_kwh,
              borderColor: PALETTE.emerald,
              backgroundColor: PALETTE.emeraldLight,
              fill: true,
              tension: 0.3,
              pointRadius: 2,
              pointHoverRadius: 5
            },
            {
              label: 'Peak Demand (kW)',
              data: data.peak_kw,
              borderColor: PALETTE.blue,
              borderDash: [5, 5],
              fill: false,
              tension: 0.2,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: { position: 'top' },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString()}`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9' },
              ticks: { callback: v => `${v.toLocaleString()}` }
            },
            x: { grid: { display: false }, ticks: { maxTicksLimit: 12 } }
          }
        }
      });
    });

  // D. Hourly Energy Consumption (Bar/Line Chart)
  fetch(`/api/charts/hourly-pattern?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartHourlyPattern').getContext('2d');
      charts.hourlyPattern = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.hours,
          datasets: [{
            label: 'Avg Hourly Load (kWh)',
            data: data.avg_kwh,
            backgroundColor: PALETTE.blue,
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9' },
              ticks: { callback: v => `${v} kWh` }
            },
            x: { grid: { display: false } }
          }
        }
      });
    });

  // E. Energy Source Distribution (Doughnut Chart)
  fetch(`/api/charts/source-distribution?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartSourceDist').getContext('2d');
      charts.sourceDist = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.sources,
          datasets: [{
            data: data.consumption_kwh,
            backgroundColor: [PALETTE.blue, PALETTE.emerald, PALETTE.amber],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          plugins: {
            legend: { position: 'bottom' },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${ctx.parsed.toLocaleString()} kWh (${data.percentages[ctx.dataIndex]}%)`
              }
            }
          }
        }
      });
    });

  // G. Occupancy vs Energy Scatter Chart
  fetch(`/api/charts/occupancy-scatter?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartOccupancyScatter').getContext('2d');
      const corrEl = document.getElementById('correlationScore');
      if (corrEl) corrEl.innerText = `r = ${data.correlation}`;

      charts.occupancyScatter = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Occupancy vs kWh',
            data: data.points,
            backgroundColor: 'rgba(14, 165, 233, 0.45)',
            borderColor: PALETTE.blue,
            borderWidth: 1,
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: ctx => {
                  const pt = ctx.raw;
                  return ` ${pt.building}: ${pt.x} occupants -> ${pt.y} kWh`;
                }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: 'Building Occupancy Count' },
              grid: { color: '#f1f5f9' }
            },
            y: {
              title: { display: true, text: 'Hourly Energy (kWh)' },
              grid: { color: '#f1f5f9' }
            }
          }
        }
      });
    });
}

// Chart Updaters
function updateBuildingChart(params) {
  fetch(`/api/charts/building-consumption?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      charts.buildingConsumption.data.labels = data.labels;
      charts.buildingConsumption.data.datasets[0].data = data.values;
      charts.buildingConsumption.data.datasets[0].backgroundColor = data.is_highest.map(h => h ? PALETTE.amber : PALETTE.emerald);
      charts.buildingConsumption.update();
    });
}

function updateDailyTrendChart(params) {
  fetch(`/api/charts/daily-trend?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      charts.dailyTrend.data.labels = data.dates;
      charts.dailyTrend.data.datasets[0].data = data.consumption_kwh;
      charts.dailyTrend.data.datasets[1].data = data.peak_kw;
      charts.dailyTrend.update();
    });
}

function updateHourlyChart(params) {
  fetch(`/api/charts/hourly-pattern?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      charts.hourlyPattern.data.datasets[0].data = data.avg_kwh;
      charts.hourlyPattern.update();
    });
}

function updateSourceChart(params) {
  fetch(`/api/charts/source-distribution?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      charts.sourceDist.data.labels = data.sources;
      charts.sourceDist.data.datasets[0].data = data.consumption_kwh;
      charts.sourceDist.update();
    });
}

function updateOccupancyScatter(params) {
  fetch(`/api/charts/occupancy-scatter?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const corrEl = document.getElementById('correlationScore');
      if (corrEl) corrEl.innerText = `r = ${data.correlation}`;
      charts.occupancyScatter.data.datasets[0].data = data.points;
      charts.occupancyScatter.update();
    });
}

// ==========================================================================
// Chart.js Visualizations: Trends Page
// ==========================================================================

function initTrendsCharts() {
  const params = getFilterParams();

  // Daily Trend
  fetch(`/api/charts/daily-trend?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartTrendsDaily').getContext('2d');
      charts.dailyTrend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.dates,
          datasets: [
            {
              label: 'Campus Consumption (kWh)',
              data: data.consumption_kwh,
              borderColor: PALETTE.emerald,
              backgroundColor: PALETTE.emeraldLight,
              fill: true,
              tension: 0.25
            },
            {
              label: 'Peak Demand (kW)',
              data: data.peak_kw,
              borderColor: PALETTE.blue,
              borderDash: [4, 4],
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
          }
        }
      });
    });

  // Monthly Comparison
  fetch(`/api/charts/monthly-trend?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartTrendsMonthly').getContext('2d');
      const datasets = [];
      let colorIdx = 0;
      for (const [bName, vals] of Object.entries(data.by_building)) {
        datasets.push({
          label: bName,
          data: vals,
          backgroundColor: PALETTE.buildingColors[colorIdx % PALETTE.buildingColors.length],
          borderRadius: 4
        });
        colorIdx++;
      }

      charts.monthlyTrend = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.months,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: {
            x: { stacked: true, grid: { display: false } },
            y: { stacked: true, grid: { color: '#f1f5f9' } }
          }
        }
      });
    });

  // Hourly Pattern
  fetch(`/api/charts/hourly-pattern?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartTrendsHourly').getContext('2d');
      charts.hourlyPattern = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.hours,
          datasets: [{
            label: 'Diurnal Hourly Profile (kWh)',
            data: data.avg_kwh,
            borderColor: PALETTE.purple,
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            fill: true,
            tension: 0.35,
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
          }
        }
      });
    });
}

function updateMonthlyTrendChart(params) {
  fetch(`/api/charts/monthly-trend?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      charts.monthlyTrend.data.labels = data.months;
      let i = 0;
      for (const [bName, vals] of Object.entries(data.by_building)) {
        if (charts.monthlyTrend.data.datasets[i]) {
          charts.monthlyTrend.data.datasets[i].data = vals;
        }
        i++;
      }
      charts.monthlyTrend.update();
    });
}

// ==========================================================================
// Chart.js Visualizations: Building Analysis Page
// ==========================================================================

function initBuildingPageCharts() {
  const params = getFilterParams();

  fetch(`/api/charts/building-peaks?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('chartBuildingPeaks').getContext('2d');
      charts.buildingPeaks = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Peak Demand (kW)',
            data: data.peak_kw,
            backgroundColor: PALETTE.red,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: '#f1f5f9' }, title: { display: true, text: 'kW' } },
            x: { grid: { display: false } }
          }
        }
      });
    });
}

function updateBuildingPeaksChart(params) {
  fetch(`/api/charts/building-peaks?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      charts.buildingPeaks.data.labels = data.labels;
      charts.buildingPeaks.data.datasets[0].data = data.peak_kw;
      charts.buildingPeaks.update();
    });
}

// ==========================================================================
// Anomaly Table Updater
// ==========================================================================

function updateAnomaliesTable(params) {
  fetch(`/api/anomalies?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('anomaliesTableBody');
      if (!tbody) return;

      tbody.innerHTML = '';
      if (!data.anomalies || data.anomalies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No statistical anomalies detected for this filter selection.</td></tr>';
        return;
      }

      data.anomalies.forEach(a => {
        let badgeClass = 'badge-sev-low';
        if (a.severity === 'Critical') badgeClass = 'badge-sev-critical';
        else if (a.severity === 'High') badgeClass = 'badge-sev-high';
        else if (a.severity === 'Medium') badgeClass = 'badge-sev-medium';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><code>${a.timestamp}</code></td>
          <td><strong>${a.building}</strong></td>
          <td class="text-danger fw-bold">${a.recorded_kwh.toFixed(1)} kWh</td>
          <td class="text-muted">${a.expected_kwh.toFixed(1)} kWh</td>
          <td><span class="badge ${badgeClass}">${a.severity}</span></td>
          <td><small class="text-danger">+${a.deviation_pct.toFixed(1)}%</small></td>
          <td><small>${a.reason}</small></td>
          <td><small class="text-secondary">${a.action_recommendation}</small></td>
        `;
        tbody.appendChild(tr);
      });
    });
}

// ==========================================================================
// Live Demonstration Handlers
// ==========================================================================

function setupDemoHandlers() {
  const btnInject = document.getElementById('btnSubmitInjectSpike');
  if (btnInject) {
    btnInject.addEventListener('click', () => {
      const building = document.getElementById('demoBuildingSelect')?.value || 'Computer Science Block';
      const spikeKwh = parseFloat(document.getElementById('demoSpikeKwh')?.value || 395.0);

      btnInject.disabled = true;
      btnInject.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Injecting Surge...';

      fetch('/api/demo/inject-spike', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ building, spike_kwh: spikeKwh })
      })
      .then(res => res.json())
      .then(resData => {
        btnInject.disabled = false;
        btnInject.innerHTML = '<i class="bi bi-lightning-charge"></i> Inject Spike';

        // Close modal if present
        const modalEl = document.getElementById('demoModal');
        if (modalEl && window.bootstrap) {
          const modalInstance = bootstrap.Modal.getInstance(modalEl);
          if (modalInstance) modalInstance.hide();
        }

        // Display Alert Callout
        const callout = document.getElementById('demoAlertCallout');
        if (callout) {
          callout.classList.remove('d-none');
          document.getElementById('demoAlertBuilding').innerText = building;
          document.getElementById('demoAlertKwh').innerText = `${spikeKwh} kWh`;
          document.getElementById('demoAlertTime').innerText = resData.injected_record.timestamp;
          document.getElementById('demoAlertAction').innerText = resData.detected_anomaly?.action_recommendation || 'Inspect electrical distribution board immediately.';
        }

        // Apply filters to trigger full dashboard visual recalculations
        applyFilters();
      })
      .catch(err => {
        console.error('Error injecting demo spike:', err);
        btnInject.disabled = false;
        btnInject.innerHTML = '<i class="bi bi-lightning-charge"></i> Inject Spike';
      });
    });
  }

  const btnReset = document.getElementById('btnResetDemoState');
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      fetch('/api/demo/reset', { method: 'POST' })
        .then(res => res.json())
        .then(() => {
          const callout = document.getElementById('demoAlertCallout');
          if (callout) callout.classList.add('d-none');
          applyFilters();
          alert('Demonstration state has been reset to baseline cleaned data.');
        });
    });
  }
}

// ==========================================================================
// Data Management: Manual Entry & CSV Upload
// ==========================================================================

function setupDataManagementHandlers() {
  // Manual Entry Form
  const manualForm = document.getElementById('manualEntryForm');
  if (manualForm) {
    manualForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(manualForm);
      const submitBtn = manualForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;

      fetch('/api/data/manual-entry', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        submitBtn.disabled = false;
        const msgEl = document.getElementById('manualEntryFeedback');
        if (data.success) {
          msgEl.className = 'alert alert-success mt-3';
          msgEl.innerText = `${data.message} Total records now: ${data.total_records.toLocaleString()}`;
          manualForm.reset();
          loadTablePage(1, 'cleaned');
        } else {
          msgEl.className = 'alert alert-danger mt-3';
          msgEl.innerText = data.error || 'Failed to add record.';
        }
        msgEl.classList.remove('d-none');
      })
      .catch(err => {
        submitBtn.disabled = false;
        console.error(err);
      });
    });
  }

  // CSV Upload Form
  const uploadForm = document.getElementById('uploadCsvForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const fileInput = document.getElementById('csvFileInput');
      if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please choose a .csv file to upload.');
        return;
      }

      const formData = new FormData(uploadForm);
      const submitBtn = uploadForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing CSV...';

      fetch('/api/data/upload', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-cloud-arrow-up"></i> Upload and Process CSV';
        const msgEl = document.getElementById('uploadFeedback');
        if (data.success) {
          msgEl.className = 'alert alert-success mt-3';
          msgEl.innerHTML = `
            <strong>Success!</strong> ${data.message}
            <br><small>Mode: ${data.mode.toUpperCase()} | Active Records: ${data.total_active_records.toLocaleString()}</small>
          `;
          loadTablePage(1, 'cleaned');
        } else {
          msgEl.className = 'alert alert-danger mt-3';
          msgEl.innerText = data.error || 'Upload failed.';
        }
        msgEl.classList.remove('d-none');
      })
      .catch(err => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-cloud-arrow-up"></i> Upload and Process CSV';
        console.error(err);
      });
    });
  }

  // Data Preview Table Pagination
  if (document.getElementById('previewTableBody')) {
    loadTablePage(1, 'cleaned');

    const viewToggle = document.getElementById('tableDatasetView');
    if (viewToggle) {
      viewToggle.addEventListener('change', () => {
        loadTablePage(1, viewToggle.value);
      });
    }
  }
}

let currentTablePage = 1;

function loadTablePage(page, viewType = 'cleaned') {
  currentTablePage = page;
  const tbody = document.getElementById('previewTableBody');
  if (!tbody) return;

  fetch(`/api/data/preview-table?page=${page}&per_page=12&view=${viewType}`)
    .then(res => res.json())
    .then(resData => {
      tbody.innerHTML = '';
      if (!resData.data || resData.data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-muted">No records found.</td></tr>';
        return;
      }

      resData.data.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><code>${r.timestamp}</code></td>
          <td><strong>${r.building}</strong></td>
          <td><small class="text-muted">${r.meter_id || '—'}</small></td>
          <td class="fw-bold">${r.units_kwh}</td>
          <td>${r.peak_kw}</td>
          <td>${r.voltage} V</td>
          <td>${r.occupancy}</td>
          <td><span class="badge ${r.source === 'Solar' ? 'badge-source-solar' : (r.source === 'Generator' ? 'badge-source-gen' : 'badge-source-grid')}">${r.source}</span></td>
          <td>${r.temperature} °C</td>
          <td><small>${r.day_type}</small></td>
        `;
        tbody.appendChild(tr);
      });

      // Update Pagination Controls
      const infoEl = document.getElementById('tablePageInfo');
      if (infoEl) infoEl.innerText = `Showing Page ${resData.page} of ${resData.total_pages} (${resData.total.toLocaleString()} total rows)`;

      const prevBtn = document.getElementById('btnTablePrev');
      const nextBtn = document.getElementById('btnTableNext');
      if (prevBtn) prevBtn.disabled = resData.page <= 1;
      if (nextBtn) nextBtn.disabled = resData.page >= resData.total_pages;
    });
}

function prevTablePage() {
  if (currentTablePage > 1) {
    const viewType = document.getElementById('tableDatasetView')?.value || 'cleaned';
    loadTablePage(currentTablePage - 1, viewType);
  }
}

function nextTablePage() {
  const viewType = document.getElementById('tableDatasetView')?.value || 'cleaned';
  loadTablePage(currentTablePage + 1, viewType);
}

