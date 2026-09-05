"use strict";

const feed = document.querySelector("#external-feed");

if (feed) {
  const status = feed.querySelector("[data-feed-status]");
  const refreshButton = feed.querySelector("[data-feed-refresh]");
  const storyList = feed.querySelector("[data-feed-list]");
  let isLoading = false;

  const safeExternalUrl = (candidate, fallback = "#") => {
    for (const value of [candidate, fallback]) {
      try {
        const url = new URL(value, window.location.origin);
        if (url.protocol === "https:" || url.protocol === "http:") {
          return url.href;
        }
      } catch (error) {
        continue;
      }
    }
    return "#";
  };

  const externalLink = (label, url, fallback) => {
    const link = document.createElement("a");
    link.textContent = label;
    link.href = safeExternalUrl(url, fallback);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    return link;
  };

  const renderStory = (story) => {
    const item = document.createElement("li");
    item.className = "external-story";

    const article = document.createElement("article");
    const heading = document.createElement("h2");
    heading.className = "external-story__title";
    heading.append(
      externalLink(story.title, story.url, story.discussion_url),
    );

    const metadata = document.createElement("p");
    metadata.className = "external-story__meta";
    const submittedAt = new Date(story.submitted_at);
    const readableTime = Number.isNaN(submittedAt.getTime())
      ? "time unavailable"
      : submittedAt.toLocaleString();
    metadata.textContent =
      `${story.source} | by ${story.submitted_by} | ${readableTime} ` +
      `| score ${story.score}`;

    const discussion = document.createElement("p");
    discussion.className = "external-story__discussion";
    discussion.append(
      externalLink(
        `View discussion (${story.comment_count} comments)`,
        story.discussion_url,
      ),
    );

    article.append(heading, metadata, discussion);
    item.append(article);
    return item;
  };

  const renderStories = (stories) => {
    storyList.replaceChildren();
    stories.forEach((story) => {
      storyList.append(renderStory(story));
    });
  };

  const loadStories = async () => {
    if (isLoading) {
      return;
    }

    isLoading = true;
    feed.setAttribute("aria-busy", "true");
    refreshButton.disabled = true;
    status.textContent = "Loading external stories...";

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
      renderStories(data.stories);
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
