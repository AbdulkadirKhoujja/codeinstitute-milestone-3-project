"use strict";

const feed = document.querySelector("#external-feed");

if (feed) {
  const status = feed.querySelector("[data-feed-status]");
  const refreshButton = feed.querySelector("[data-feed-refresh]");
  let isLoading = false;

  const loadStories = async () => {
    if (isLoading) {
      return;
    }

    isLoading = true;
    feed.setAttribute("aria-busy", "true");
    refreshButton.disabled = true;
    status.textContent = "Loading external stories…";

    try {
      const response = await fetch(feed.dataset.feedUrl, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        cache: "no-store",
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.success || !Array.isArray(data.stories)) {
        throw new Error(
          data.message || "External stories are temporarily unavailable.",
        );
      }
      status.textContent = `${data.stories.length} external stories loaded.`;
    } catch (error) {
      status.textContent =
        error.message || "External stories are temporarily unavailable.";
    } finally {
      isLoading = false;
      feed.removeAttribute("aria-busy");
      refreshButton.disabled = false;
    }
  };

  refreshButton.addEventListener("click", loadStories);
  loadStories();
}
