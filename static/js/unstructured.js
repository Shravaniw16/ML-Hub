let uploadedFilePath = null;

const form = document.getElementById("unstructuredForm");
const statusMsg = document.getElementById("statusMsg");
const previewBox = document.getElementById("previewBox");
const downloadBtn = document.getElementById("downloadCsvBtn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("textFile");

  if (!fileInput.files.length) {
    alert("Please select a file");
    return;
  }

  statusMsg.innerText = "Uploading file...";
  previewBox.style.display = "none";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  /* ======================
     STEP 1: UPLOAD FILE
     ====================== */
  const uploadRes = await fetch("/upload-unstructured", {
    method: "POST",
    body: formData
  });

  const uploadData = await uploadRes.json();

  if (uploadData.error) {
    alert(uploadData.error);
    return;
  }

  uploadedFilePath = uploadData.filepath;
  statusMsg.innerText = "File uploaded. Cleaning data...";

  /* ======================
     STEP 2: CLEAN DATA
     ====================== */
  const cleanRes = await fetch("/clean-unstructured", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filepath: uploadedFilePath
    })
  });

  const cleanData = await cleanRes.json();

  if (cleanData.error) {
    alert(cleanData.error);
    return;
  }

  statusMsg.innerText =
    `Cleaning complete. Total records: ${cleanData.total_records}`;

  /* ======================
     SHOW PREVIEW
     ====================== */
  previewBox.innerHTML = "<b>Preview (First 5 rows):</b><br><br>";

  cleanData.preview.slice(0, 5).forEach(row => {
    previewBox.innerHTML += `
      <div>
        <b>Original:</b> ${row.original_text}<br>
        <b>Cleaned:</b> ${row.cleaned_text}<br>
        <b>Words:</b> ${row.word_count},
        <b>Chars:</b> ${row.char_count}
        <hr>
      </div>
    `;
  });

  previewBox.style.display = "block";

  /* Enable download button */
  downloadBtn.disabled = false;
});


/* ======================
   STEP 3: DOWNLOAD CSV
   ====================== */
downloadBtn.addEventListener("click", async () => {

  if (!uploadedFilePath) {
    alert("No cleaned data available");
    return;
  }

  statusMsg.innerText = "Preparing clean CSV for download...";

  const res = await fetch("/download-clean-csv", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filepath: uploadedFilePath
    })
  });

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "cleaned_unstructured_data.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(url);

  statusMsg.innerText = "Clean CSV downloaded successfully";
});
