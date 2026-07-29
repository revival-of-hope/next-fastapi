import { defineConfig } from "@hey-api/openapi-ts"

export default defineConfig({
  input: "http://localhost:8000/api/openapi.json",
  output: "lib/api/generated",
  plugins: [
    {
      name: "@hey-api/client-next",
      runtimeConfigPath: "./lib/api/hey-api",
    },
  ],
})
