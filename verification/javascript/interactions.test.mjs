import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { setImmediate } from "node:timers/promises";
import test from "node:test";
import { JSDOM } from "jsdom";

// Only project scripts execute. Network responses and DOM fixtures are simulated.
const scripts = Object.fromEntries(["voting", "external-feed"].map((name) => [
  name, readFileSync(new URL(`../../static/js/${name}.js`, import.meta.url), "utf8"),
]));
const votingMarkup = `<section class="vote-panel">
  <p id="vote-score">Score 0</p><div data-vote-controls>
  ${[1, -1].map((value) => `<form action="/posts/1/vote/" data-vote-form>
    <input name="csrfmiddlewaretoken" value="test-token">
    <input name="value" value="${value}">
    <button data-vote-value="${value}" aria-pressed="false">Vote</button>
  </form>`).join("")}</div><p data-vote-feedback class="visually-hidden"></p>
</section>`;
const feedMarkup = `<div id="external-feed" data-feed-url="/discover/feed/">
  <p data-feed-status></p><button data-feed-refresh>Refresh</button>
  <ol data-feed-list></ol></div>`;
const story = {
  title: "<img src=x onerror=alert(1)>", url: "javascript:alert(1)",
  discussion_url: "https://news.ycombinator.com/item?id=1", source: "example.com",
  submitted_by: "sample", submitted_at: "2026-09-08T10:00:00Z",
  score: 3, comment_count: 2,
};
const response = (data, ok = true) => ({ ok, json: async () => data });

function setup(t, name, fetch) {
  const dom = new JSDOM(name === "voting" ? votingMarkup : feedMarkup, {
    url: "https://byteboard.example/", runScripts: "outside-only",
  });
  t.after(() => dom.window.close());
  dom.window.fetch = fetch;
  dom.window.eval(scripts[name]);
  return dom.window;
}

function submit(window, index = 0) {
  window.document.querySelectorAll("form")[index].dispatchEvent(
    new window.Event("submit", { bubbles: true, cancelable: true }),
  );
}

test("voting sends CSRF and form data, updates score/pressed state", async (t) => {
  let request;
  const window = setup(t, "voting", async (url, options) => {
    request = { url, options };
    return response({ success: true, score: 1, current_vote: 1, message: "Recorded" });
  });
  submit(window);
  assert.ok(window.document.querySelector("button").disabled);
  await setImmediate();
  assert.equal(request.url, "https://byteboard.example/posts/1/vote/");
  assert.equal(request.options.headers["X-CSRFToken"], "test-token");
  assert.equal(request.options.body.get("value"), "1");
  assert.equal(window.document.querySelector("#vote-score").textContent, "Score 1");
  assert.equal(window.document.querySelector("button").getAttribute("aria-pressed"), "true");
  assert.equal(window.document.querySelector("button").disabled, false);
});

test("voting rejects duplicate submissions while busy", async (t) => {
  let calls = 0;
  let finish;
  const window = setup(t, "voting", () => {
    calls += 1;
    return new Promise((resolve) => { finish = resolve; });
  });
  submit(window);
  submit(window, 1);
  assert.equal(calls, 1);
  finish(response({ success: true, score: 1, current_vote: 1, message: "Recorded" }));
  await setImmediate();
});

test("voting restores controls and retains score after authentication failure", async (t) => {
  const window = setup(t, "voting", async () => response({ message: "Log in to vote." }, false));
  submit(window);
  await setImmediate();
  assert.equal(window.document.querySelector("#vote-score").textContent, "Score 0");
  assert.equal(window.document.querySelector("[data-vote-feedback]").textContent, "Log in to vote.");
  assert.equal(window.document.querySelector("button").disabled, false);
});

test("voting rejects malformed success without corrupting displayed state", async (t) => {
  const window = setup(t, "voting", async () => response({}));
  submit(window);
  await setImmediate();
  assert.equal(window.document.querySelector("#vote-score").textContent, "Score 0");
  assert.match(window.document.querySelector("[data-vote-feedback]").textContent, /unavailable/);
  assert.equal(window.document.querySelector("button").disabled, false);
});

test("feed loads hostile text safely, keeps safe fallback links and allows refresh", async (t) => {
  let calls = 0;
  const window = setup(t, "external-feed", async () => {
    calls += 1;
    return response({ success: true, stories: [story] });
  });
  assert.ok(window.document.querySelector("button").disabled);
  await setImmediate();
  const document = window.document;
  assert.equal(document.querySelector("h2").textContent, `${story.title} (opens in a new tab)`);
  const links = document.querySelectorAll("a");
  assert.equal(links[0].getAttribute("aria-label"), `${story.title} (opens in a new tab)`);
  assert.equal(links[1].getAttribute("aria-label"), "View discussion (2 comments) (opens in a new tab)");
  for (const link of links) {
    assert.equal(link.target, "_blank");
    assert.equal(link.querySelector(".visually-hidden").textContent, " (opens in a new tab)");
  }
  assert.equal(document.querySelector("img"), null);
  assert.equal(document.querySelector("a").href, story.discussion_url);
  assert.equal(document.querySelector("a").rel, "noopener noreferrer");
  assert.equal(document.querySelector("button").disabled, false);
  document.querySelector("button").click();
  await setImmediate();
  assert.equal(calls, 2);
});

test("feed failure restores controls and retry can recover to an empty state", async (t) => {
  let calls = 0;
  const window = setup(t, "external-feed", async () => {
    if (++calls === 1) throw new Error("Simulated network failure");
    return response({ success: true, stories: [] });
  });
  await setImmediate();
  const document = window.document;
  assert.match(document.querySelector("[data-feed-status]").textContent, /unavailable/);
  document.querySelector("button").click();
  await setImmediate();
  assert.match(document.querySelector("[data-feed-status]").textContent, /No external stories/);
  assert.equal(document.querySelector("#external-feed").hasAttribute("aria-busy"), false);
});

test("feed rejects malformed story records with useful feedback", async (t) => {
  const window = setup(t, "external-feed", async () => response({ success: true, stories: [{}] }));
  await setImmediate();
  assert.match(window.document.querySelector("[data-feed-status]").textContent, /unavailable/);
  assert.equal(window.document.querySelector("h2"), null);
  assert.equal(window.document.querySelector("button").disabled, false);
});

test("partial feed announces partial state and prevents overlapping refreshes", async (t) => {
  let calls = 0;
  let finish;
  const window = setup(t, "external-feed", () => {
    calls += 1;
    return new Promise((resolve) => { finish = resolve; });
  });
  window.document.querySelector("button").dispatchEvent(new window.Event("click"));
  assert.equal(calls, 1);
  finish(response({ success: true, stories: [story], partial: true, message: "Some items unavailable." }));
  await setImmediate();
  assert.match(window.document.querySelector("[data-feed-status]").textContent, /Some items unavailable/);
});
