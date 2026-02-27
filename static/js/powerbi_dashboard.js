let pieChart, barChart, donutChart, lineChart;

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("fileInput");

  if (!fileInput.files.length) {
    alert("Please select a CSV file");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch("/upload", {
    method: "POST",
    body: formData
  });

  if (!res.ok) {
    alert("Upload failed");
    return;
  }

  const data = await res.json();
  renderDashboard(data);
});

/* ===============================
   RENDER DASHBOARD
================================ */
function renderDashboard(data) {

  document.getElementById("totalRows").innerText = data.total_rows;
  document.getElementById("totalColumns").innerText = data.total_columns;

  /* ---- CATEGORY COUNTS ---- */
  const labelColumn = data.columns[data.columns.length - 1];
  const counts = {};

  data.preview.forEach(row => {
    const val = row[labelColumn];
    counts[val] = (counts[val] || 0) + 1;
  });

  const labels = Object.keys(counts);
  const values = Object.values(counts);

  destroyCharts();

  /* ---- PIE ---- */
  pieChart = new Chart(document.getElementById("pieChart"), {
    type: "pie",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: ["#2563eb", "#22c55e", "#f97316", "#a855f7"]
      }]
    },
    options: { plugins: { legend: { position: "right" } } }
  });

  /* ---- BAR ---- */
  barChart = new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Count",
        data: values,
        backgroundColor: "#3b82f6"
      }]
    },
    options: { plugins: { legend: { display: false } } }
  });

  /* ---- DONUT ---- */
  donutChart = new Chart(document.getElementById("donutChart"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: ["#ef4444", "#22c55e", "#6366f1"]
      }]
    },
    options: { cutout: "70%" }
  });

  /* ---- LINE ---- */
  lineChart = new Chart(document.getElementById("lineChart"), {
    type: "line",
    data: {
      labels: values.map((_, i) => `Point ${i + 1}`),
      datasets: [{
        label: "Trend",
        data: values,
        borderColor: "#6366f1",
        tension: 0.4,
        fill: false
      }]
    }
  });
}

/* ===============================
   DOWNLOAD DASHBOARD
================================ */
document.getElementById("downloadDashboardBtn").addEventListener("click", () => {
  html2canvas(document.getElementById("dashboard")).then(canvas => {
    const link = document.createElement("a");
    link.download = "powerbi_dashboard.png";
    link.href = canvas.toDataURL();
    link.click();
  });
});

/* ===============================
   CLEAN OLD CHARTS
================================ */
function destroyCharts() {
  if (pieChart) pieChart.destroy();
  if (barChart) barChart.destroy();
  if (donutChart) donutChart.destroy();
  if (lineChart) lineChart.destroy();
}
