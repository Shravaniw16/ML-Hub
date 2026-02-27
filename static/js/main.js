document.addEventListener("DOMContentLoaded", () => {

  /* ==============================
     INDEX.HTML (UPLOAD PAGE)
     ============================== */

  const uploadForm = document.getElementById("uploadForm");

  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const fileInput = document.getElementById("fileInput");

      if (!fileInput || !fileInput.files.length) {
        alert("Please select a file");
        return;
      }

      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("/upload", {
          method: "POST",
          body: formData,
          credentials: "include"
        });

        const data = await response.json();

        /* ==============================
           FILE TYPE HANDLING
           ============================== */

        // ✅ CSV DATASET
        if (!data.type && data.preview) {
          localStorage.setItem("analysisData", JSON.stringify(data));
          localStorage.setItem("datasetPath", data.filepath);
          localStorage.setItem("columns", JSON.stringify(data.columns));

          window.location.href = "/analysis-page";
        }

        // 🔊 AUDIO FILE
        else if (data.type === "audio") {

  const loudness =
    data.rms_energy && data.rms_energy > 0
      ? data.rms_energy
      : "Very Low / Silence";

  alert(`
Audio Analysis:
File: ${data.filename}
Duration: ${data.duration_seconds} seconds
Sample Rate: ${data.sample_rate} Hz
RMS Energy (Loudness): ${loudness}
`);
}


        // 🎥 VIDEO FILE
        else if (data.type === "video") {
          alert(`
Video Analysis:
File: ${data.filename}
Duration: ${data.duration_seconds} seconds
FPS: ${data.fps}
Resolution: ${data.resolution}
Total Frames: ${data.total_frames}
`);
        }

        else {
          alert("Unknown file type or invalid response");
        }

      } catch (error) {
        console.error(error);
        alert("Upload failed. Is backend running?");
      }
    });
  }

  /* ==============================
     ANALYSIS.HTML (CSV DASHBOARD)
     ============================== */

  const previewHead = document.getElementById("previewHead");
  const previewBody = document.getElementById("previewBody");

  if (previewHead && previewBody) {
    const stored = localStorage.getItem("analysisData");
    if (!stored) return;

    const data = JSON.parse(stored);
    if (!data.preview || data.preview.length === 0) return;

    // TABLE HEADERS
    previewHead.innerHTML = "";
    Object.keys(data.preview[0]).forEach(col => {
      previewHead.innerHTML += `<th>${col}</th>`;
    });

    // TABLE ROWS
    previewBody.innerHTML = "";
    data.preview.forEach(row => {
      let tr = "<tr>";
      Object.values(row).forEach(val => {
        tr += `<td>${val}</td>`;
      });
      tr += "</tr>";
      previewBody.innerHTML += tr;
    });
  }

  /* ==============================
     PROCEED TO TRAINING
     ============================== */

  window.goToTraining = function () {
    const data = localStorage.getItem("analysisData");
    if (!data) {
      alert("Please upload and analyze a CSV dataset first");
      return;
    }
    window.location.href = "train.html";
  };

});
