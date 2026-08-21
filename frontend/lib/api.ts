import {
  apiLoginAccessPost,
  apiUserMeGet,
  apiUserMeMessagesGet,
  apiUserRegisterPost,
} from "@/lib/api/generated/sdk.gen"
import type {
  ChatMessagePublic,
  Token,
  UserPublic,
} from "@/lib/api/generated/types.gen"

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "")

type ApiErrorShape = {
  detail?: string | Array<{ msg?: string }>
  message?: string
}

export function getApiErrorMessage(
  error: unknown,
  fallback = "请求失败，请稍后重试。",
): string {
  if (typeof error === "string" && error.trim()) return error

  if (error && typeof error === "object") {
    const candidate = error as ApiErrorShape
    if (typeof candidate.detail === "string") return candidate.detail
    if (Array.isArray(candidate.detail)) {
      const message = candidate.detail
        .map((item) => item?.msg)
        .filter(Boolean)
        .join("；")
      if (message) return message
    }
    if (typeof candidate.message === "string") return candidate.message
  }

  return fallback
}

export async function registerUser(
  name: string,
  password: string,
): Promise<UserPublic> {
  const result = await apiUserRegisterPost({
    baseUrl: API_BASE_URL,
    body: { name, password },
    throwOnError: true,
  })
  return result.data
}

export async function loginUser(
  name: string,
  password: string,
): Promise<Token> {
  const result = await apiLoginAccessPost({
    baseUrl: API_BASE_URL,
    body: {
      username: name,
      password,
      grant_type: "password",
      scope: "",
    },
    throwOnError: true,
  })
  return result.data
}

export async function getCurrentUser(token: string): Promise<UserPublic> {
  const result = await apiUserMeGet({
    baseUrl: API_BASE_URL,
    auth: token,
    throwOnError: true,
  })
  return result.data
}

export async function getMessageHistory(
  token: string,
  options: { offset?: number; limit?: number } = {},
): Promise<ChatMessagePublic[]> {
  const result = await apiUserMeMessagesGet({
    baseUrl: API_BASE_URL,
    auth: token,
    query: {
      offset: options.offset ?? 0,
      limit: options.limit ?? 20,
    },
    throwOnError: true,
  })
  return result.data
}

export async function streamChat(
  token: string,
  userMessage: string,
  signal?: AbortSignal,
): Promise<Response> {
  const query = new URLSearchParams({ user_message: userMessage })
  const response = await fetch(`${API_BASE_URL}/api/user/me/chat?${query}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "text/plain",
    },
    signal,
  })

  if (!response.ok) {
    let detail: unknown
    try {
      detail = await response.json()
    } catch {
      detail = await response.text()
    }
    throw new Error(getApiErrorMessage(detail, `请求失败（${response.status}）`))
  }

  return response
}
