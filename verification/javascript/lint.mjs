import { fileURLToPath } from "node:url";
import { ESLint } from "eslint";

const linter = new ESLint({
  cwd: fileURLToPath(new URL("../../", import.meta.url)),
  overrideConfigFile: fileURLToPath(new URL("eslint.config.mjs", import.meta.url)),
});
const results = await linter.lintFiles([
  "static/js/*.js", "verification/javascript/*.mjs",
]);
const formatter = await linter.loadFormatter("stylish");
console.log(formatter.format(results));
if (results.some((result) => result.errorCount || result.warningCount)) {
  throw new Error("JavaScript lint must pass without errors or warnings.");
}
console.log(`Linted ${results.length} JavaScript files without errors or warnings.`);
