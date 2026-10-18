// Block D, INV-010. Scope: the critical domain only (never the default "all the code").
// Run through `npm run mutation` (wrapper: tools/harness/run_mutation.sh) or `npx stryker run` directly.
export default {
  testRunner: "vitest",
  mutate: [
    "src/connections/domain/**/*.ts",
    "src/connections/application/**/*.ts",
    "!src/**/*.test.ts",
  ],
  // Default mutator set on purpose: widen only if the score plateaus artificially high.
  reporters: ["clear-text", "html", "json"],
  htmlReporter: { fileName: "reports/mutation/mutation.html" },
  jsonReporter: { fileName: "reports/mutation/mutation.json" },
  // No blocking threshold here: the harness wrapper owns it (tools/harness/mutation-threshold.json).
  thresholds: { high: 90, low: 75, break: null },
  incremental: true,
  incrementalFile: "reports/mutation/stryker-incremental.json",
  concurrency: 2,
  timeoutMS: 10000,
  // Exclude an equivalent mutant only with a comment saying which behavior it does not change:
  // mutator: { excludedMutations: [] },
};
