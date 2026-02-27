document.addEventListener("DOMContentLoaded", async () => {

  const tbody = document.getElementById("modelsBody");
  tbody.innerHTML = "<tr><td colspan='7'>Loading...</td></tr>";

  try {
    const response = await fetch("/my-models", {
      method: "GET",
      credentials: "include"   // 🔥 REQUIRED
    });

    if (response.status === 401) {
      alert("Session expired. Please login again.");
      window.location.href = "/login-page";
      return;
    }

    const models = await response.json();

    if (!models.length) {
      tbody.innerHTML = "<tr><td colspan='7'>No models trained yet</td></tr>";
      return;
    }

    tbody.innerHTML = "";

    models.forEach(m => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${m.dataset_name}</td>
        <td>${m.model_type}</td>
        <td>${m.accuracy ?? "--"}</td>
        <td>${m.precision ?? "--"}</td>
        <td>${m.recall ?? "--"}</td>
        <td>${m.f1 ?? "--"}</td>
        <td>${m.created_at ?? "--"}</td>
      `;
      tbody.appendChild(row);
    });

  } catch (err) {
    console.error(err);
    tbody.innerHTML = "<tr><td colspan='7'>Error loading models</td></tr>";
  }
});
