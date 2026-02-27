document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/dashboard", {
      credentials: "include"
    });

    if (res.status === 401) {
      window.location.href = "/login-page";
      return;
    }

    const data = await res.json();

    document.getElementById("datasets").innerText =
      data.total_datasets ?? 0;

    document.getElementById("models").innerText =
      data.total_models ?? 0;

    document.getElementById("accuracy").innerText =
      data.best_accuracy ? data.best_accuracy + "%" : "--";

    document.getElementById("lastModel").innerText =
      data.last_model
        ? `${data.last_model.model_type}`
        : "None";

  } catch (err) {
    console.error(err);
  }
});
