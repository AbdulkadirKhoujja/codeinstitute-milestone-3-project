import js from "@eslint/js";

export default [
  {
    files: ["**/*.js", "**/*.mjs"],
    rules: {
      ...js.configs.recommended.rules,
      eqeqeq: ["error", "always"],
      "no-var": "error",
      "prefer-const": "error",
    },
    languageOptions: {
      ecmaVersion: 2022,
      globals: {
        document: "readonly", window: "readonly", fetch: "readonly",
        FormData: "readonly", URL: "readonly",
        console: "readonly",
      },
    },
  },
];
