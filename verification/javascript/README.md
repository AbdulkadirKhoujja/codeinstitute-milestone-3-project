# JavaScript interaction verification

From this directory run `npm ci --ignore-scripts`, `npm test` and `npm run lint`.
Node 22.13 or later in the Node 22 series is supported by the pinned ESLint 10.

The Node test runner and jsdom execute ByteBoard's own scripts against small
DOM fixtures, with simulated fetch responses and no live API requests.
Fixtures contain dummy tokens and sample text, not real sessions. These tests
cover event handling, state transitions, safe rendering, retry and failures.
They do not contact Django, prove server writes, execute Bootstrap or establish
browser layout, keyboard, console, network or accessibility results.

Eight checks were added during Phase 4. Initially five passed and three failed:
duplicate vote events issued two requests, malformed voting JSON displayed
`Score undefined`, and an empty story object rendered as a successful feed.
The corrections validate response shapes before rendering and guard busy votes.
All eight then passed. Thirteen related Django tests also passed.

ESLint uses its recommended rules, strict equality, no `var`, and `prefer-const`.
Browser globals are explicitly read-only. No recommended rule is disabled.
The lint runner treats warnings, including skipped files, as failures.

Tools: [Node test runner](https://nodejs.org/api/test.html),
[jsdom](https://github.com/jsdom/jsdom) (MIT), and
[ESLint](https://eslint.org/) (MIT). Node 22.15.0 and jsdom 26.1.0 were used on
Windows on 8 September 2026. jsdom 26 supports this installed Node version.
