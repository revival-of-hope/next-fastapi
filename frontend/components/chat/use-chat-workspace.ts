"use client"

import * as React from "react"
import { useRouter } from "next/navigation"

import {
  getApiErrorMessage,
  getConversations,
  getCurrentUser,
  getMessages,
  isAuthenticationError,
  streamChat,
} from "@/lib/api"
import type {
  ConversationPublic,
  MessagePublic,
  MessageRole,
  UserPublic,
} from "@/lib/api-types"
import { clearAccessToken, getAccessToken } from "@/lib/auth"

export type UiMessage = {
  id: string
  role: MessageRole
  content: string
  createdAt?: string
  status?: "streaming" | "interrupted" | "failed"
}

function toUiMessages(messages: MessagePublic[]): UiMessage[] {
  return messages.map((message) => ({
    id: `message-${message.message_id}`,
    role: message.role,
    content: message.content,
    createdAt: message.created_at,
  }))
}

function localMessageId(role: MessageRole): string {
  const suffix =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`
  return `${role}-${suffix}`
}

function conversationIdFromResponse(response: Response): number | null {
  const value = Number(response.headers.get("X-Conversation-ID"))
  return Number.isSafeInteger(value) && value > 0 ? value : null
}

export function useChatWorkspace() {
  const router = useRouter()
  const [user, setUser] = React.useState<UserPublic | null>(null)
  const [conversations, setConversations] = React.useState<
    ConversationPublic[]
  >([])
  const [activeConversationId, setActiveConversationId] = React.useState<
    number | null
  >(null)
  const [messages, setMessages] = React.useState<UiMessage[]>([])
  const [booting, setBooting] = React.useState(true)
  const [loadingMessages, setLoadingMessages] = React.useState(false)
  const [refreshingConversations, setRefreshingConversations] =
    React.useState(false)
  const [sending, setSending] = React.useState(false)
  const [error, setError] = React.useState("")
  const tokenRef = React.useRef<string | null>(null)
  const abortRef = React.useRef<AbortController | null>(null)
  const messageRequestRef = React.useRef(0)

  const redirectToLogin = React.useCallback(() => {
    abortRef.current?.abort()
    clearAccessToken()
    router.replace("/user/login")
  }, [router])

  const handleAuthenticationError = React.useCallback(
    (requestError: unknown): boolean => {
      if (!isAuthenticationError(requestError)) return false
      redirectToLogin()
      return true
    },
    [redirectToLogin]
  )

  const refreshConversations = React.useCallback(
    async (accessToken: string) => {
      setRefreshingConversations(true)
      try {
        const items = await getConversations(accessToken, { limit: 100 })
        setConversations(items)
        return items
      } finally {
        setRefreshingConversations(false)
      }
    },
    []
  )

  React.useEffect(() => {
    const accessToken = getAccessToken()
    if (!accessToken) {
      redirectToLogin()
      return
    }

    const authenticatedToken = accessToken
    let active = true
    tokenRef.current = authenticatedToken

    async function initialize() {
      try {
        const [currentUser, conversationItems] = await Promise.all([
          getCurrentUser(authenticatedToken),
          getConversations(authenticatedToken, { limit: 100 }),
        ])
        if (!active) return

        setUser(currentUser)
        setConversations(conversationItems)

        const firstConversation = conversationItems[0]
        if (!firstConversation) return

        setActiveConversationId(firstConversation.conversation_id)
        setLoadingMessages(true)
        try {
          const storedMessages = await getMessages(
            authenticatedToken,
            firstConversation.conversation_id,
            { limit: 200 }
          )
          if (active) setMessages(toUiMessages(storedMessages))
        } finally {
          if (active) setLoadingMessages(false)
        }
      } catch (requestError) {
        if (!active || handleAuthenticationError(requestError)) return
        setError(
          getApiErrorMessage(requestError, "工作空间加载失败，请稍后重试。")
        )
      } finally {
        if (active) setBooting(false)
      }
    }

    void initialize()
    return () => {
      active = false
      abortRef.current?.abort()
    }
  }, [handleAuthenticationError, redirectToLogin])

  const openConversation = React.useCallback(
    async (conversationId: number) => {
      const accessToken = tokenRef.current
      if (!accessToken || sending) return

      const requestId = messageRequestRef.current + 1
      messageRequestRef.current = requestId
      setActiveConversationId(conversationId)
      setMessages([])
      setError("")
      setLoadingMessages(true)

      try {
        const storedMessages = await getMessages(accessToken, conversationId, {
          limit: 200,
        })
        if (messageRequestRef.current === requestId) {
          setMessages(toUiMessages(storedMessages))
        }
      } catch (requestError) {
        if (handleAuthenticationError(requestError)) return
        if (messageRequestRef.current === requestId) {
          setError(getApiErrorMessage(requestError, "对话内容加载失败。"))
        }
      } finally {
        if (messageRequestRef.current === requestId) setLoadingMessages(false)
      }
    },
    [handleAuthenticationError, sending]
  )

  const startNewChat = React.useCallback(() => {
    if (sending) return
    messageRequestRef.current += 1
    setActiveConversationId(null)
    setMessages([])
    setLoadingMessages(false)
    setError("")
  }, [sending])

  const sendMessage = React.useCallback(
    async (rawContent: string) => {
      const content = rawContent.trim()
      const accessToken = tokenRef.current
      if (!content || !accessToken || sending) return false
      const authenticatedToken = accessToken
      if (content.length > 20_000) {
        setError("单条消息不能超过 20,000 个字符。")
        return false
      }

      const conversationIdAtSend = activeConversationId
      const userMessageId = localMessageId("user")
      const assistantMessageId = localMessageId("assistant")
      let responseConversationId: number | null = null

      setError("")
      setSending(true)
      setMessages((current) => [
        ...current,
        { id: userMessageId, role: "user", content },
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          status: "streaming",
        },
      ])

      const controller = new AbortController()
      abortRef.current = controller

      async function synchronizeConversations() {
        try {
          const items = await refreshConversations(authenticatedToken)
          const resolvedConversationId =
            conversationIdAtSend ??
            responseConversationId ??
            items[0]?.conversation_id ??
            null
          if (resolvedConversationId !== null) {
            setActiveConversationId(resolvedConversationId)
          }
        } catch (requestError) {
          if (!handleAuthenticationError(requestError)) {
            setError("消息已处理，但会话列表刷新失败。")
          }
        }
      }

      try {
        const response = await streamChat(
          authenticatedToken,
          {
            conversation_id: conversationIdAtSend,
            content,
          },
          controller.signal
        )
        responseConversationId = conversationIdFromResponse(response)
        if (!response.body) throw new Error("服务端没有返回可读取的数据流。")

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let receivedContent = false

        while (true) {
          const { value, done } = await reader.read()
          if (done) {
            const tail = decoder.decode()
            if (tail) {
              receivedContent = true
              setMessages((current) =>
                current.map((message) =>
                  message.id === assistantMessageId
                    ? { ...message, content: message.content + tail }
                    : message
                )
              )
            }
            break
          }
          if (!value) continue

          const chunk = decoder.decode(value, { stream: true })
          if (!chunk) continue
          receivedContent = true
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantMessageId
                ? { ...message, content: message.content + chunk }
                : message
            )
          )
        }

        if (!receivedContent) throw new Error("服务端返回了空内容。")
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantMessageId
              ? { ...message, status: undefined }
              : message
          )
        )
        await synchronizeConversations()
      } catch (requestError) {
        if (controller.signal.aborted) {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantMessageId
                ? {
                    ...message,
                    content: message.content || "已停止生成。",
                    status: "interrupted",
                  }
                : message
            )
          )
          await synchronizeConversations()
          return true
        }

        if (handleAuthenticationError(requestError)) return false
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantMessageId
              ? {
                  ...message,
                  content: message.content || "回答生成失败。",
                  status: "failed",
                }
              : message
          )
        )
        setError(getApiErrorMessage(requestError, "发送失败，请稍后重试。"))
        await synchronizeConversations()
      } finally {
        if (abortRef.current === controller) abortRef.current = null
        setSending(false)
      }

      return true
    },
    [
      activeConversationId,
      handleAuthenticationError,
      refreshConversations,
      sending,
    ]
  )

  const logout = React.useCallback(() => {
    abortRef.current?.abort()
    tokenRef.current = null
    clearAccessToken()
    router.replace("/")
  }, [router])

  const activeConversation = React.useMemo(
    () =>
      conversations.find(
        (conversation) => conversation.conversation_id === activeConversationId
      ) ?? null,
    [activeConversationId, conversations]
  )

  return {
    user,
    conversations,
    activeConversation,
    activeConversationId,
    messages,
    booting,
    loadingMessages,
    refreshingConversations,
    sending,
    error,
    clearError: () => setError(""),
    openConversation,
    startNewChat,
    sendMessage,
    stopGenerating: () => abortRef.current?.abort(),
    logout,
  }
}
