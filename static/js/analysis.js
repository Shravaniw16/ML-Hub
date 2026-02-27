document.addEventListener("DOMContentLoaded", () => {

  /* ==============================
     LOAD ANALYSIS DATA
     ============================== */
  const stored = localStorage.getItem("analysisData");

  if (!stored) {
    alert("No analysis data found. Please upload a dataset first.");
    window.location.href = "/";
    return;
  }

  const data = JSON.parse(stored);

  /* ==============================
     SUMMARY CARDS (CSV ONLY)
     ============================== */
  if (data.total_rows !== undefined) {
    document.getElementById("totalRows").innerText = data.total_rows;
    document.getElementById("totalColumns").innerText = data.total_columns;
    document.getElementById("missingPercent").innerText =
      data.missing_percent !== undefined ? data.missing_percent + "%" : "--";
    document.getElementById("duplicateRows").innerText =
      data.duplicate_rows ?? "--";
    document.getElementById("healthScore").innerText =
      data.health_score !== undefined ? data.health_score + " / 100" : "--";
  }

  /* ==============================
     DATASET PREVIEW TABLE
     ============================== */
  const head = document.getElementById("previewHead");
  const body = document.getElementById("previewBody");

  head.innerHTML = "";
  body.innerHTML = "";

  if (data.preview && data.preview.length > 0) {
    Object.keys(data.preview[0]).forEach(col => {
      const th = document.createElement("th");
      th.innerText = col;
      head.appendChild(th);
    });

    data.preview.forEach(row => {
      const tr = document.createElement("tr");
      Object.values(row).forEach(val => {
        const td = document.createElement("td");
        td.innerText = val;
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
  } else {
    body.innerHTML = "<tr><td colspan='100%'>No preview data available</td></tr>";
  }

  /* ==============================
     CHARTS (CSV)
     ============================== */
  const chartGrid = document.getElementById("chartGrid");
  if (chartGrid) {
    chartGrid.innerHTML = "";

    if (data.charts && data.charts.length > 0) {
      data.charts.forEach(src => {
        const card = document.createElement("div");
        card.className = "img-card";

        const img = document.createElement("img");
        img.src = src;
        img.alt = "Chart";

        card.appendChild(img);
        chartGrid.appendChild(card);
      });
    } else {
      chartGrid.innerHTML = "<p>No charts generated</p>";
    }
  }

  /* ==============================
     AUDIO ANALYSIS
     ============================== */
  if (data.type === "audio") {
    document.getElementById("audioSection").style.display = "block";
    document.getElementById("audioDuration").innerText =
      data.duration_seconds + " s";
    document.getElementById("audioSampleRate").innerText =
      data.sample_rate + " Hz";
    document.getElementById("audioChannels").innerText = data.channels;
    document.getElementById("audioLoudness").innerText =
      data.loudness_rms ?? "N/A";
    document.getElementById("audioZCR").innerText =
      data.zero_crossing_rate ?? "N/A";
  }

  /* ==============================
     VIDEO ANALYSIS
     ============================== */
  if (data.type === "video") {
    document.getElementById("videoSection").style.display = "block";
    document.getElementById("videoDuration").innerText =
      data.duration_seconds + " s";
    document.getElementById("videoFPS").innerText = data.fps;
    document.getElementById("videoResolution").innerText = data.resolution;
    document.getElementById("videoFrames").innerText =
      data.frames ?? "N/A";
  }

  /* ==============================
     DATA CLEANING
     ============================== */
  const cleanBtn = document.getElementById("cleanDataBtn");
  const downloadBtn = document.getElementById("downloadCleanBtn");
  const statusText = document.getElementById("cleanStatus");

  let cleanedFilePath = null;

  if (cleanBtn) {
    cleanBtn.addEventListener("click", async () => {
      statusText.innerText = "Cleaning data...";

      const datasetPath = data.filepath;

      const res = await fetch("/clean-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filepath: datasetPath })
      });

      const result = await res.json();

      if (result.error) {
        statusText.innerText = result.error;
        return;
      }

      cleanedFilePath = result.cleaned_path;
      statusText.innerText = "Data cleaned successfully!";
      downloadBtn.disabled = false;
    });
  }

  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      if (!cleanedFilePath) {
        alert("Please clean the data first");
        return;
      }
      window.location.href =
        `/download-clean-data?path=${encodeURIComponent(cleanedFilePath)}`;
    });
  }

});
const cleanUnBtn = document.getElementById("cleanUnstructuredBtn");
const downloadUnBtn = document.getElementById("downloadCleanUnstructuredBtn");
const status = document.getElementById("cleanStatus");

let cleanedPath = null;

if (cleanUnBtn) {
  cleanUnBtn.addEventListener("click", async () => {
    status.innerText = "Cleaning sentiment data...";

    const stored = localStorage.getItem("analysisData");
    const data = JSON.parse(stored);

    const res = await fetch("/download-clean-csv", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filepath: data.filepath })
    });

    if (!res.ok) {
      status.innerText = "Cleaning failed";
      return;
    }

    const blob = await res.blob();

    // Force download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sentiment_cleaned.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();

    status.innerText = "✅ Cleaned data downloaded (labels converted to 0/1)";
  });
}
async function cleanData() {
  const datasetPath = localStorage.getItem("datasetPath");

  if (!datasetPath) {
    alert("No dataset path found. Upload dataset first.");
    return;
  }

  const res = await fetch("/download-clean-csv", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ filepath: datasetPath })
  });

  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  alert("✅ Dataset cleaned successfully!");

  // 🔥 VERY IMPORTANT
  localStorage.setItem("cleanedReady", "true");
}
