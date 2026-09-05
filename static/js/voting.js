"use strict";

document.querySelectorAll("[data-vote-form]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const panel = form.closest(".vote-panel");
    const controls = panel.querySelector("[data-vote-controls]");
    const buttons = controls.querySelectorAll("button[data-vote-value]");
    const feedback = panel.querySelector("[data-vote-feedback]");
    const score = panel.querySelector("#vote-score");
    const csrfToken = form.querySelector(
      "input[name='csrfmiddlewaretoken']",
    ).value;

    controls.setAttribute("aria-busy", "true");
    buttons.forEach((button) => {
      button.disabled = true;
    });

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.message || "Voting is temporarily unavailable.");
      }

      score.textContent = `Score ${data.score}`;
      buttons.forEach((button) => {
        const isCurrent = String(data.current_vote) === button.dataset.voteValue;
        button.setAttribute("aria-pressed", String(isCurrent));
      });
      feedback.textContent = data.message;
    } catch (error) {
      feedback.textContent = error.message || "Voting is temporarily unavailable.";
    } finally {
      feedback.classList.remove("visually-hidden");
      controls.removeAttribute("aria-busy");
      buttons.forEach((button) => {
        button.disabled = false;
      });
    }
  });
});
