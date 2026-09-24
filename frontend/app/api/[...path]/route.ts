import type { NextRequest } from "next/server"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ path: string[] }> }

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  const backend = (process.env.API_BASE_URL || "http://backend:8000").replace(
    /\/$/,
    ""
  )
  const url = `${backend}/api/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`
  const headers = new Headers()
  for (const name of ["authorization", "accept", "content-type"]) {
    const value = request.headers.get(name)
    if (value) headers.set(name, value)
  }
  try {
    const upstream = await fetch(url, {
      method: request.method,
      headers,
      body: request.method === "GET" ? undefined : await request.arrayBuffer(),
      cache: "no-store",
    })
    const responseHeaders = new Headers()
    for (const name of [
      "content-type",
      "cache-control",
      "x-conversation-id",
      "content-disposition",
    ]) {
      const value = upstream.headers.get(name)
      if (value) responseHeaders.set(name, value)
    }
    responseHeaders.set("cache-control", "no-store")
    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders,
    })
  } catch {
    return Response.json({ detail: "Backend unavailable" }, { status: 502 })
  }
}

export const GET = proxy
export const POST = proxy
export const DELETE = proxy
