import { apiRoutes } from "@/lib/api/generated/routes"
import type {
  ChatRequest,
  ConversationPublic,
  MessagePublic,
  Token,
  UsagePublic,
  UserPublic,
  UsersPublic,
} from "@/lib/api-types"

// Same-origin requests are forwarded by Next.js. This preserves streaming headers
// and works when the backend runs on a Docker-only hostname.
const BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "")
type ApiErrorBody = {
  detail?: string | Array<{ msg?: string }>
  message?: string
}
const translations: Record<string, string> = {
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
function errorText(body: unknown): string | null {
  if (typeof body === "string") return translations[body] ?? body
  if (!body || typeof body !== "object") return null
  const candidate = body as ApiErrorBody
  const detail = Array.isArray(candidate.detail)
    ? candidate.detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join("；")
    : candidate.detail
  const message = detail || candidate.message
  return message ? (translations[message] ?? message) : null
}
async function apiError(response: Response): Promise<ApiError> {
  const raw = await response.text()
  let body: unknown = raw
  try {
    body = JSON.parse(raw) as unknown
  } catch {
    /* plain text */
  }
  return new ApiError(
    errorText(body) ?? `请求失败（HTTP ${response.status}）`,
    response.status,
    body
  )
}
async function request<T>(
  path: string,
  init: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set("Accept", "application/json")
  if (token) headers.set("Authorization", `Bearer ${token}`)
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  })
  if (!response.ok) throw await apiError(response)
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
export function getApiErrorMessage(
  error: unknown,
  fallback = "请求失败，请稍后重试。"
): string {
  if (error instanceof TypeError && /fetch|network/i.test(error.message)) {
    return "无法连接后端服务，请检查 API_BASE_URL 与后端运行状态。"
  }
  return error instanceof Error ? error.message : (errorText(error) ?? fallback)
}
export function isAuthenticationError(error: unknown): boolean {
  return error instanceof ApiError && [401, 403].includes(error.status)
}
export function registerUser(
  name: string,
  password: string
): Promise<UserPublic> {
  return request<UserPublic>(apiRoutes.ApiUsersRegisterPost, {
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
  })
  return request<Token>(apiRoutes.ApiAccessPost, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  })
}
export function getCurrentUser(token: string): Promise<UserPublic> {
  return request<UserPublic>(apiRoutes.ApiUsersMeGet, {}, token)
}
export function getConversations(
  token: string,
  options: { offset?: number; limit?: number } = {}
): Promise<ConversationPublic[]> {
  const query = new URLSearchParams({
    offset: String(options.offset ?? 0),
    limit: String(options.limit ?? 100),
  })
  return request<ConversationPublic[]>(
    `${apiRoutes.ApiConversationsGet}?${query}`,
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
  return request<MessagePublic[]>(
    `${apiRoutes.ApiMessagesGet}?${query}`,
    {},
    token
  )
}
export async function streamChat(
  token: string,
  payload: ChatRequest,
  signal?: AbortSignal
): Promise<Response> {
  const response = await fetch(`${BASE_URL}${apiRoutes.ApiMessagesPost}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "text/plain",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
    signal,
  })
  if (!response.ok) throw await apiError(response)
  return response
}
export function getUsers(
  token: string,
  skip = 0,
  limit = 100
): Promise<UsersPublic> {
  return request<UsersPublic>(
    `${apiRoutes.ApiUsersGet}?${new URLSearchParams({ skip: String(skip), limit: String(limit) })}`,
    {},
    token
  )
}
export function getUsage(token: string): Promise<UsagePublic> {
  return request<UsagePublic>(apiRoutes.ApiUsersUsageGet, {}, token)
}
export function deleteUser(token: string, id: number): Promise<void> {
  return request<void>(
    apiRoutes.ApiUsersByuserDelete.replace("{user_id}", String(id)),
    { method: "DELETE" },
    token
  )
}
