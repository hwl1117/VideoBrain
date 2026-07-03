import nextVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const eslintConfig = [
  ...nextVitals,
  ...nextTypescript,
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
      "react-hooks/immutability": "off",
      "react-hooks/set-state-in-effect": "off",
    },
    ignores: [
      ".next/**",
      "node_modules/**",
      "out/**",
      "*.config.js",
    ],
  },
];

export default eslintConfig;
