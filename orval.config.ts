import { defineConfig } from "orval";

export default defineConfig({
  logos: {
    input: "packages/contracts/openapi.json",
    output: {
      target: "packages/client-ts/src/client/generated.ts",
      client: "fetch",
      clean: true,
      baseUrl: "/api",
      override: {
        fetch: {
          forceSuccessResponse: true,
        },
      },
    },
  },
});
