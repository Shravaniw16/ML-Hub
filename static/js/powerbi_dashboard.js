let pieChart, barChart, donutChart, lineChart;

/* ===============================
UPLOAD DATASET
================================ */
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
DETECT COLUMN TYPES
================================ */
function detectColumns(data){

  const sample = data.preview[0];
  const numeric = [];
  const categorical = [];

  Object.keys(sample).forEach(col => {

    const values = data.preview.map(r => r[col]);

    const isNumeric = values.every(v => !isNaN(parseFloat(v)));

    if(isNumeric){
      numeric.push(col);
    }else{
      const unique = [...new Set(values)];
      if(unique.length <= 10){
        categorical.push(col);
      }
    }

  });

  return {numeric, categorical};

}


/* ===============================
RENDER DASHBOARD
================================ */
function renderDashboard(data){

  document.getElementById("totalRows").innerText = data.total_rows;
  document.getElementById("totalColumns").innerText = data.total_columns;

  destroyCharts();

  const {numeric, categorical} = detectColumns(data);

  /* -------------------------
     CATEGORICAL CHARTS
  ------------------------- */

  if(categorical.length > 0){

    const col = categorical[0];

    const counts = {};
    data.preview.forEach(row=>{
      const val = row[col];
      counts[val] = (counts[val] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const values = Object.values(counts);

    /* PIE CHART */
    pieChart = new Chart(document.getElementById("pieChart"),{
      type:"pie",
      data:{
        labels,
        datasets:[{
          data:values,
          backgroundColor:["#2563eb","#22c55e","#f97316","#a855f7","#e11d48"]
        }]
      },
      options:{
        plugins:{legend:{position:"right"}}
      }
    });

    /* BAR CHART */
    barChart = new Chart(document.getElementById("barChart"),{
      type:"bar",
      data:{
        labels,
        datasets:[{
          label:`${col} Count`,
          data:values,
          backgroundColor:"#3b82f6"
        }]
      }
    });

    /* DONUT */
    donutChart = new Chart(document.getElementById("donutChart"),{
      type:"doughnut",
      data:{
        labels,
        datasets:[{
          data:values,
          backgroundColor:["#ef4444","#22c55e","#6366f1","#f59e0b"]
        }]
      },
      options:{cutout:"65%"}
    });

  }


  /* -------------------------
     NUMERIC CHART
  ------------------------- */

  if(numeric.length > 0){

    const col = numeric[0];

    const values = data.preview.map(r => Number(r[col]));

    lineChart = new Chart(document.getElementById("lineChart"),{
      type:"line",
      data:{
        labels: values.map((_,i)=>`Row ${i+1}`),
        datasets:[{
          label:`${col} Trend`,
          data:values,
          borderColor:"#6366f1",
          tension:0.4,
          fill:false
        }]
      }
    });

  }

}


/* ===============================
DOWNLOAD DASHBOARD
================================ */
document.getElementById("downloadDashboardBtn")
.addEventListener("click",()=>{

  html2canvas(document.getElementById("dashboard"))
  .then(canvas=>{
    const link=document.createElement("a");
    link.download="powerbi_dashboard.png";
    link.href=canvas.toDataURL();
    link.click();
  });

});


/* ===============================
DESTROY OLD CHARTS
================================ */
function destroyCharts(){

  if(pieChart) pieChart.destroy();
  if(barChart) barChart.destroy();
  if(donutChart) donutChart.destroy();
  if(lineChart) lineChart.destroy();

}