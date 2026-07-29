import type { Config } from "./generated/client/types.gen"

export const createClientConfig = (config: Config): Config => ({
  ...config,

  baseUrl: "http://localhost:8000",
})
