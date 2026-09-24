import { readFile, writeFile } from "node:fs/promises"
import { fileURLToPath } from "node:url"
import { dirname, resolve } from "node:path"
import openapiTS, { astToString } from "openapi-typescript"

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const output = resolve(root, "lib/api/generated")
const source = process.env.OPENAPI_URL
const spec = source
  ? await fetch(source).then((response) => {
      if (!response.ok) throw new Error(`OpenAPI HTTP ${response.status}`)
      return response.json()
    })
  : JSON.parse(await readFile(resolve(output, "openapi.json"), "utf8"))

if (!spec.paths || !Object.keys(spec.paths).length) {
  throw new Error("OpenAPI 文档中没有可用路径")
}

const paths = Object.entries(spec.paths).flatMap(([path, methods]) =>
  Object.entries(methods)
    .filter(
      ([method, operation]) =>
        ["get", "post", "put", "patch", "delete"].includes(method) &&
        operation.operationId
    )
    .map(([method, operation]) => [
      operation.operationId,
      path,
      method.toUpperCase(),
    ])
)
if (new Set(paths.map(([id]) => id)).size !== paths.length) {
  throw new Error("OpenAPI operationId 有重复，无法生成唯一的路由映射")
}

await writeFile(
  resolve(output, "openapi.json"),
  JSON.stringify(spec, null, 2) + "\n"
)
await writeFile(
  resolve(output, "schema.ts"),
  astToString(await openapiTS(spec))
)
await writeFile(
  resolve(output, "routes.ts"),
  `// Generated from /api/openapi.json. Run pnpm generate:api to refresh.\n` +
    `export const apiRoutes = ${JSON.stringify(Object.fromEntries(paths.map(([id, path]) => [id, path])), null, 2)} as const\n` +
    `export const apiMethods = ${JSON.stringify(Object.fromEntries(paths.map(([id, , method]) => [id, method])), null, 2)} as const\n`
)
console.log(
  `Generated ${paths.length} API operations from ${source || "lib/api/generated/openapi.json"}`
)
