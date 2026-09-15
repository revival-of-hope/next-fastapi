import type {
  ChatRequest,
  ConversationPublic,
  MessagePublic,
  Token,
  UserPublic,
} from "@/lib/api-types"

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "")

type ApiErrorBody = {
  detail?: string | Array<{ msg?: string }>
  message?: string
}

const errorTranslations: Record<string, string> = {
  "Incorrect name or password": "用户名或密码错误。",
  "Inactive user": "当前账户已停用。",
  "Invalid credentials": "登录状态已失效，请重新登录。",
  "User Not Found": "用户不存在。",
  "Name already exists": "用户名已存在。",
  "Conversation not found": "该对话不存在或无权访问。",
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly body?: unknown
  ) {
    super(message)
    this.name = "ApiError"
  }
}

function localizeErrorMessage(message: string): string {
  return errorTranslations[message] ?? message
}

function messageFromBody(body: unknown): string | null {
  if (typeof body === "string" && body.trim()) {
    return localizeErrorMessage(body.trim())
  }

  if (!body || typeof body !== "object") return null

  const candidate = body as ApiErrorBody
  if (typeof candidate.detail === "string" && candidate.detail.trim()) {
    return localizeErrorMessage(candidate.detail.trim())
  }
  if (Array.isArray(candidate.detail)) {
    const message = candidate.detail
      .map((item) => item?.msg)
      .filter((item): item is string => Boolean(item))
      .join("；")
    if (message) return message
  }
  if (typeof candidate.message === "string" && candidate.message.trim()) {
    return localizeErrorMessage(candidate.message.trim())
  }

  return null
}

async function readResponseBody(response: Response): Promise<unknown> {
  const text = await response.text()
  if (!text) return null

  try {
    return JSON.parse(text) as unknown
  } catch {
    return text
  }
}

async function createApiError(response: Response): Promise<ApiError> {
  const body = await readResponseBody(response)
  const message = messageFromBody(body) ?? `请求失败（HTTP ${response.status}）`
  return new ApiError(message, response.status, body)
}

async function requestJson<T>(
  path: string,
  init: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set("Accept", "application/json")
  if (token) headers.set("Authorization", `Bearer ${token}`)

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  })

  if (!response.ok) throw await createApiError(response)
  return (await response.json()) as T
}

export function getApiErrorMessage(
  error: unknown,
  fallback = "请求失败，请稍后重试。"
): string {
  if (error instanceof TypeError && error.message === "Failed to fetch") {
    return "无法连接后端服务，请检查服务地址或网络状态。"
  }
  if (error instanceof Error && error.message.trim()) return error.message
  return messageFromBody(error) ?? fallback
}

export function isAuthenticationError(error: unknown): boolean {
  return (
    error instanceof ApiError && (error.status === 401 || error.status === 403)
  )
}

export function registerUser(
  name: string,
  password: string
): Promise<UserPublic> {
  return requestJson<UserPublic>("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, password }),
  })
}

export function loginUser(name: string, password: string): Promise<Token> {
  const body = new URLSearchParams({
    username: name,
    password,
    grant_type: "password",
    scope: "",
  })

  return requestJson<Token>("/api/access-token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  })
}

export function getCurrentUser(token: string): Promise<UserPublic> {
  return requestJson<UserPublic>("/api/users/me", {}, token)
}

export function getConversations(
  token: string,
  options: { offset?: number; limit?: number } = {}
): Promise<ConversationPublic[]> {
  const query = new URLSearchParams({
    offset: String(options.offset ?? 0),
    limit: String(options.limit ?? 100),
  })
  return requestJson<ConversationPublic[]>(
    `/api/conversations?${query}`,
    {},
    token
  )
}

export function getMessages(
  token: string,
  conversationId: number,
  options: { offset?: number; limit?: number } = {}
): Promise<MessagePublic[]> {
  const query = new URLSearchParams({
    conversation_id: String(conversationId),
    offset: String(options.offset ?? 0),
    limit: String(options.limit ?? 200),
  })
  return requestJson<MessagePublic[]>(`/api/messages?${query}`, {}, token)
}

export async function streamChat(
  token: string,
  request: ChatRequest,
  signal?: AbortSignal
): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}/api/messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "text/plain",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
    cache: "no-store",
    signal,
  })

  if (!response.ok) throw await createApiError(response)
  return response
}
