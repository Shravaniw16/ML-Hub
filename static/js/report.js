document.addEventListener("DOMContentLoaded", () => {

  const stored = localStorage.getItem("trainingResult");

  if (!stored) {
    alert("No training result found.");
    window.location.href = "/train-page";
    return;
  }

  const result = JSON.parse(stored);

  // ===== SUMMARY METRICS =====
  document.getElementById("accuracy").innerText =
    result.accuracy ? result.accuracy + " %" : "--";

  document.getElementById("precision").innerText =
    result.precision ?? "--";

  document.getElementById("recall").innerText =
    result.recall ?? "--";

  document.getElementById("f1score").innerText =
    result.f1 ?? "--";

  // ===== METRICS TABLE =====
  const tbody = document.getElementById("metricsTableBody");
  tbody.innerHTML = "";

  Object.keys(result).forEach(key => {
    if (
      !["model", "confusion_matrix", "feature_importance"].includes(key)
    ) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${key.toUpperCase()}</td>
        <td>${result[key]}</td>
      `;
      tbody.appendChild(row);
    }
  });

  // ===== CONFUSION MATRIX =====
  if (result.confusion_matrix) {
    const cmImg = document.getElementById("confusionMatrix");
    cmImg.src = result.confusion_matrix;
    cmImg.style.display = "block";
  }

  // ===== FEATURE IMPORTANCE =====
  const fiSection = document.getElementById("featureImportanceSection");
  const fiImg = document.getElementById("featureImportance");

  if (result.feature_importance) {
    fiImg.src = result.feature_importance;
    fiImg.style.display = "block";
  } else {
    fiSection.innerHTML += `
      <p style="color:#666;font-style:italic;">
        Feature importance is available only for Random Forest models.
      </p>
    `;
  }

});

// ===== DOWNLOAD PDF =====
function downloadReport() {
  window.open("/download-report", "_blank");
}
const explanationList = document.getElementById("explanationList");

if (result.explanations) {
  explanationList.innerHTML = "";

  Object.entries(result.explanations).forEach(([key, text]) => {
    const li = document.createElement("li");
    li.innerHTML = `<b>${key.replace("_", " ").toUpperCase()}:</b> ${text}`;
    explanationList.appendChild(li);
  });
}
