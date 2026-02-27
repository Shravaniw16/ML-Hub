fetch("/dashboard-dataset-data", { credentials: "include" })
  .then(res => res.json())
  .then(data => {

    if (data.error) {
      alert(data.error);
      return;
    }

    // KPI CARDS
    document.getElementById("totalRows").innerText = data.total_rows;
    document.getElementById("totalColumns").innerText = data.total_columns;

    // LABEL DISTRIBUTION
    const labels = Object.keys(data.label_distribution || {});
    const values = Object.values(data.label_distribution || {});

    // BAR CHART
    new Chart(document.getElementById("barChart"), {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Count",
          data: values,
          backgroundColor: ["#4f46e5", "#ef4444"]
        }]
      }
    });

    // PIE CHART
    new Chart(document.getElementById("pieChart"), {
      type: "pie",
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: ["#4f46e5", "#ef4444"]
        }]
      }
    });

  });

function downloadCleaned() {
  window.location.href = "/download-clean-csv";
}
