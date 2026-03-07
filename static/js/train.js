function suggestTarget(columns) {
  const keywords = ["target","label","class","churn","outcome","result","Survived"];

  // check column names first
  for (let col of columns) {
    const lower = col.toLowerCase();
    if (keywords.some(k => lower.includes(k))) {
      return col;
    }
  }

  // fallback: choose column with few categories
  return columns[columns.length - 1];
}
document.addEventListener("DOMContentLoaded", () => {

  /* =========================
     LOAD COLUMNS
  ========================= */
  const columns = JSON.parse(localStorage.getItem("columns"));
const targetSelect = document.getElementById("targetColumn");

if (columns && targetSelect) {

  columns.forEach(col => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.textContent = col;
    targetSelect.appendChild(opt);
  });

  // ⭐ AUTO TARGET SUGGESTION
  const suggested = suggestTarget(columns);
  if (suggested) {
    targetSelect.value = suggested;
  }

}

  /* =========================
     MODEL OPTIONS
  ========================= */
  const modelRadios = document.querySelectorAll('input[name="modelType"]');
  const modelSelect = document.getElementById("modelSelect");

  function populateModels(type) {

  modelSelect.innerHTML = `<option value="">-- Choose Model --</option>`;

  if (type === "classification") {

    modelSelect.innerHTML += `
      <option value="logistic">Logistic Regression</option>
      <option value="random_forest">Random Forest</option>
      <option value="knn">K-Nearest Neighbors</option>
    `;

  }

  if (type === "regression") {

    modelSelect.innerHTML += `
      <option value="linear">Linear Regression</option>
      <option value="random_forest_reg">Random Forest Regressor</option>
    `;

  }

  /* ⭐ ADD THIS PART */

  if (type === "clustering") {

    modelSelect.innerHTML += `
      <option value="kmeans">K-Means Clustering</option>
      <option value="dbscan">DBSCAN Clustering</option>
      <option value="hierarchical">Hierarchical Clustering</option>
    `;

  }

}

  modelRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      populateModels(radio.value);
    });
  });

  // ✅ AUTO-FIRE DEFAULT SELECTION
  const checked = document.querySelector('input[name="modelType"]:checked');
  if (checked) {
    populateModels(checked.value);
  }
});

/* =========================
   START TRAINING
========================= */
async function startTraining() {

  const filepath =
  localStorage.getItem("cleanedPath") ||
  localStorage.getItem("datasetPath");

  const target = document.getElementById("targetColumn").value;
  const model = document.getElementById("modelSelect").value;
  const typeChecked = document.querySelector('input[name="modelType"]:checked');

  if (!filepath) return alert("Dataset missing");
  if (!target) return alert("Select target column");
  if (!typeChecked) return alert("Select prediction type");
  if (!model) return alert("Select model");

  document.getElementById("loadingBox").style.display = "block";

  try {
    const res = await fetch("/train", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ filepath, target, model })
    });

    const data = await res.json();
    document.getElementById("loadingBox").style.display = "none";

    if (data.error) return alert(data.error);

    localStorage.setItem("trainingResult", JSON.stringify(data));
    window.location.href = "/report-page";

  } catch (err) {
    console.error(err);
    alert("Training failed");
    document.getElementById("loadingBox").style.display = "none";
  }
}
