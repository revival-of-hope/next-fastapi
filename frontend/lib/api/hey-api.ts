import type { Config } from "./generated/client/types.gen"

export const createClientConfig = (config: Config): Config => ({
  ...config,
  baseUrl: (process.env.NEXT_PUBLIC_API_BASE_URL ?? config.baseUrl ?? "http://localhost:8000").replace(/\/$/, ""),
})
