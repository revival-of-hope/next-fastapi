"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import {
  Bot,
  Clock3,
  History,
  LoaderCircle,
  LogOut,
  Menu,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  SendHorizontal,
  Sparkles,
  UserRound,
  X,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import {
  getApiErrorMessage,
  getCurrentUser,
  getMessageHistory,
  streamChat,
} from "@/lib/api"
import type { ChatMessagePublic, UserPublic } from "@/lib/api/generated/types.gen"
import { clearAccessToken, getAccessToken } from "@/lib/auth"
import { cn } from "@/lib/utils"

type UiMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  pending?: boolean
  historical?: boolean
}

function formatHistoryTime(value: string | null) {
  if (!value) return "历史回复"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return "历史回复"

  const now = new Date()
  const sameDay = now.toDateString() === date.toDateString()
  return new Intl.DateTimeFormat("zh-CN", {
    ...(sameDay ? {} : { month: "numeric", day: "numeric" }),
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date)
}

function historyPreview(content: string | null) {
  const compact = (content ?? "").replace(/\s+/g, " ").trim()
  return compact || "空回复"
}

export function ChatShell() {
  const router = useRouter()
  const [token, setToken] = React.useState<string | null>(null)
  const [user, setUser] = React.useState<UserPublic | null>(null)
  const [history, setHistory] = React.useState<ChatMessagePublic[]>([])
  const [messages, setMessages] = React.useState<UiMessage[]>([])
  const [input, setInput] = React.useState("")
  const [loadingPage, setLoadingPage] = React.useState(true)
  const [loadingHistory, setLoadingHistory] = React.useState(false)
  const [sending, setSending] = React.useState(false)
  const [error, setError] = React.useState("")
  const [sidebarOpen, setSidebarOpen] = React.useState(true)
  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)
  const scrollRef = React.useRef<HTMLDivElement>(null)
  const abortRef = React.useRef<AbortController | null>(null)

  const loadHistory = React.useCallback(async (accessToken: string) => {
    setLoadingHistory(true)
    try {
      const items = await getMessageHistory(accessToken, { limit: 20 })
      setHistory(items)
    } catch (err) {
      setError(getApiErrorMessage(err, "历史记录加载失败。"))
    } finally {
      setLoadingHistory(false)
    }
  }, [])

  React.useEffect(() => {
    const accessToken = getAccessToken()
    if (!accessToken) {
      router.replace("/user/login")
      return
    }

    setToken(accessToken)
    void (async () => {
      try {
        const currentUser = await getCurrentUser(accessToken)
        setUser(currentUser)

        try {
          const items = await getMessageHistory(accessToken, { limit: 20 })
          setHistory(items)
        } catch (err) {
          setError(getApiErrorMessage(err, "历史记录加载失败。"))
        }
      } catch {
        clearAccessToken()
        router.replace("/user/login")
      } finally {
        setLoadingPage(false)
      }
    })()
  }, [router])

  React.useEffect(() => {
    const viewport = scrollRef.current
    if (!viewport) return
    viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" })
  }, [messages])

  React.useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return
    textarea.style.height = "0px"
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`
  }, [input])

  function logout() {
    abortRef.current?.abort()
    clearAccessToken()
    router.replace("/")
  }

  function startNewChat() {
    abortRef.current?.abort()
    setMessages([])
    setError("")
    setInput("")
    setMobileSidebarOpen(false)
    window.setTimeout(() => textareaRef.current?.focus(), 0)
  }

  function openHistory(item: ChatMessagePublic) {
    setMessages([
      {
        id: `history-${item.chat_id}`,
        role: "assistant",
        content: item.content ?? "",
        historical: true,
      },
    ])
    setMobileSidebarOpen(false)
  }

  async function submitMessage() {
    const content = input.trim()
    if (!content || !token || sending) return

    setError("")
    setInput("")
    setSending(true)

    const userId = `user-${Date.now()}`
    const assistantId = `assistant-${Date.now()}`
    setMessages((current) => [
      ...current,
      { id: userId, role: "user", content },
      { id: assistantId, role: "assistant", content: "", pending: true },
    ])

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const response = await streamChat(token, content, controller.signal)
      if (!response.body) throw new Error("服务端没有返回可读取的数据流。")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let completed = false

      while (!completed) {
        const { value, done } = await reader.read()
        completed = done
        if (!value) continue

        const chunk = decoder.decode(value, { stream: !done })
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId
              ? { ...message, content: message.content + chunk, pending: !done }
              : message,
          ),
        )
      }

      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId ? { ...message, pending: false } : message,
        ),
      )
      await loadHistory(token)
    } catch (err) {
      if (controller.signal.aborted) {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: message.content || "已停止生成。",
                  pending: false,
                }
              : message,
          ),
        )
        return
      }
      setMessages((current) => current.filter((message) => message.id !== assistantId))
      setError(getApiErrorMessage(err, "发送失败，请稍后重试。"))
    } finally {
      if (abortRef.current === controller) abortRef.current = null
      setSending(false)
      window.setTimeout(() => textareaRef.current?.focus(), 0)
    }
  }

  function handleComposerKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void submitMessage()
    }
  }

  if (loadingPage) {
    return (
      <main className="grid min-h-svh place-items-center bg-background">
        <div className="flex flex-col items-center gap-3 text-sm text-muted-foreground">
          <span className="grid size-11 place-items-center rounded-2xl bg-primary/10 text-primary">
            <LoaderCircle className="size-5 animate-spin" />
          </span>
          正在进入你的工作空间…
        </div>
      </main>
    )
  }

  return (
    <main className="flex h-svh overflow-hidden bg-background">
      {mobileSidebarOpen && (
        <button
          aria-label="关闭侧栏"
          className="fixed inset-0 z-40 bg-black/35 backdrop-blur-[1px] lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-[288px] flex-col border-r bg-sidebar transition-transform duration-200 lg:relative lg:z-auto lg:shrink-0",
          mobileSidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
          sidebarOpen ? "lg:w-[288px]" : "lg:w-[76px]",
        )}
      >
        <div className="flex h-16 shrink-0 items-center justify-between px-3.5">
          <div className={cn("flex min-w-0 items-center gap-2.5", !sidebarOpen && "lg:justify-center lg:w-full")}>
            <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm shadow-primary/20">
              <Bot className="size-5" />
            </span>
            <div className={cn("min-w-0 transition-opacity", !sidebarOpen && "lg:hidden")}>
              <div className="truncate font-heading text-sm font-semibold">Agent Studio</div>
              <div className="truncate text-[11px] text-muted-foreground">AI workspace</div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="关闭侧栏"
            onClick={() => setMobileSidebarOpen(false)}
            className="lg:hidden"
          >
            <X className="size-4" />
          </Button>
        </div>

        <div className="px-3 pb-3">
          <Button
            variant="outline"
            className={cn("h-10 w-full justify-start rounded-xl bg-background/70 shadow-none", !sidebarOpen && "lg:justify-center lg:px-0")}
            onClick={startNewChat}
          >
            <Plus className="size-4" />
            <span className={cn(!sidebarOpen && "lg:hidden")}>新对话</span>
          </Button>
        </div>

        <div className={cn("flex items-center gap-2 px-4 pb-2 text-[11px] font-medium tracking-wide text-muted-foreground uppercase", !sidebarOpen && "lg:justify-center lg:px-2")}>
          <History className="size-3.5" />
          <span className={cn(!sidebarOpen && "lg:hidden")}>历史回复</span>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-2.5 pb-3 [scrollbar-width:thin]">
          {loadingHistory ? (
            <div className="grid place-items-center py-8 text-muted-foreground">
              <LoaderCircle className="size-4 animate-spin" />
            </div>
          ) : history.length === 0 ? (
            <div className={cn("mx-1 rounded-xl border border-dashed px-3 py-5 text-center text-xs leading-5 text-muted-foreground", !sidebarOpen && "lg:hidden")}>
              暂无历史回复。发送第一条消息后会出现在这里。
            </div>
          ) : (
            <div className="space-y-1">
              {history.map((item) => (
                <button
                  key={item.chat_id}
                  type="button"
                  title={historyPreview(item.content)}
                  onClick={() => openHistory(item)}
                  className={cn(
                    "group flex w-full items-start gap-2.5 rounded-xl px-2.5 py-2.5 text-left text-sm transition hover:bg-sidebar-accent",
                    !sidebarOpen && "lg:justify-center lg:px-2",
                  )}
                >
                  <MessageSquareText className="mt-0.5 size-4 shrink-0 text-muted-foreground transition group-hover:text-foreground" />
                  <span className={cn("min-w-0 flex-1", !sidebarOpen && "lg:hidden")}>
                    <span className="block truncate text-[13px] font-medium text-sidebar-foreground/90">
                      {historyPreview(item.content)}
                    </span>
                    <span className="mt-0.5 flex items-center gap-1 text-[10px] text-muted-foreground">
                      <Clock3 className="size-2.5" />
                      {formatHistoryTime(item.created_at)}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="border-t p-3">
          <div className={cn("flex items-center gap-2.5 rounded-xl px-2 py-2", !sidebarOpen && "lg:justify-center lg:px-0")}>
            <span className="grid size-8 shrink-0 place-items-center rounded-full bg-primary/10 text-primary">
              <UserRound className="size-4" />
            </span>
            <div className={cn("min-w-0 flex-1", !sidebarOpen && "lg:hidden")}>
              <div className="truncate text-xs font-medium">{user?.name || "用户"}</div>
              <div className="text-[10px] text-muted-foreground">已登录</div>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="退出登录"
              title="退出登录"
              onClick={logout}
              className={cn(!sidebarOpen && "lg:hidden")}
            >
              <LogOut className="size-3.5" />
            </Button>
          </div>
        </div>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col bg-background">
        <header className="flex h-16 shrink-0 items-center justify-between border-b px-3 sm:px-5">
          <div className="flex items-center gap-1.5">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full lg:hidden"
              aria-label="打开侧栏"
              onClick={() => setMobileSidebarOpen(true)}
            >
              <Menu className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="hidden rounded-full lg:inline-flex"
              aria-label={sidebarOpen ? "收起侧栏" : "展开侧栏"}
              onClick={() => setSidebarOpen((value) => !value)}
            >
              {sidebarOpen ? <PanelLeftClose className="size-4" /> : <PanelLeftOpen className="size-4" />}
            </Button>
            <div className="ml-1">
              <div className="font-heading text-sm font-semibold">智能体对话</div>
              <div className="hidden text-[11px] text-muted-foreground sm:block">实时流式回复 · 自动保存历史</div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <ThemeToggle />
            <Button variant="ghost" size="icon" className="rounded-full lg:hidden" onClick={logout} aria-label="退出登录">
              <LogOut className="size-4" />
            </Button>
          </div>
        </header>

        <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto [scrollbar-width:thin]">
          <div className="mx-auto flex min-h-full w-full max-w-4xl flex-col px-4 py-8 sm:px-8 sm:py-10">
            {messages.length === 0 ? (
              <div className="my-auto flex flex-col items-center py-12 text-center">
                <div className="relative mb-6">
                  <div className="absolute inset-0 rounded-3xl bg-primary/15 blur-2xl" />
                  <div className="relative grid size-16 place-items-center rounded-3xl border bg-card shadow-sm">
                    <Sparkles className="size-7 text-primary" />
                  </div>
                </div>
                <h1 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
                  今天想讨论什么？
                </h1>
                <p className="mt-3 max-w-lg text-sm leading-6 text-muted-foreground sm:text-base">
                  输入问题开始新的对话。回答将实时生成，并在完成后自动加入左侧历史记录。
                </p>
                <div className="mt-8 grid w-full max-w-2xl gap-3 sm:grid-cols-2">
                  {["帮我梳理一个复杂问题的思路", "把这段想法整理成清晰的结构", "解释一个我正在学习的概念", "为下一步工作列出可执行方案"].map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => {
                        setInput(suggestion)
                        textareaRef.current?.focus()
                      }}
                      className="rounded-2xl border bg-card/60 px-4 py-3.5 text-left text-sm leading-5 text-muted-foreground transition hover:-translate-y-0.5 hover:border-primary/25 hover:bg-card hover:text-foreground hover:shadow-sm"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-8 pb-8">
                {messages.map((message) => (
                  <article key={message.id} className={cn("flex gap-3 sm:gap-4", message.role === "user" && "justify-end")}>
                    {message.role === "assistant" && (
                      <span className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                        <Bot className="size-4" />
                      </span>
                    )}
                    <div
                      className={cn(
                        "max-w-[85%] whitespace-pre-wrap text-sm leading-7 sm:max-w-[78%] sm:text-[15px]",
                        message.role === "user"
                          ? "rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-primary-foreground shadow-sm"
                          : "min-w-0 pt-0.5 text-foreground/90",
                      )}
                    >
                      {message.historical && (
                        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border bg-muted/45 px-2.5 py-1 text-[10px] font-medium text-muted-foreground">
                          <History className="size-3" /> 历史回复
                        </div>
                      )}
                      <div>
                        {message.content}
                        {message.pending && (
                          <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded-full bg-primary align-middle" />
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>

        <footer className="shrink-0 bg-gradient-to-t from-background via-background to-background/0 px-3 pb-3 pt-2 sm:px-6 sm:pb-5">
          <div className="mx-auto max-w-4xl">
            {error && (
              <div className="mb-2 flex items-center justify-between gap-3 rounded-xl border border-destructive/20 bg-destructive/5 px-3 py-2 text-xs text-destructive">
                <span>{error}</span>
                <button type="button" onClick={() => setError("")} className="shrink-0 rounded-md p-1 hover:bg-destructive/10" aria-label="关闭错误提示">
                  <X className="size-3.5" />
                </button>
              </div>
            )}
            <div className="rounded-[1.4rem] border bg-card p-2 shadow-[0_10px_40px_-18px_color-mix(in_oklch,var(--foreground)_22%,transparent)] transition focus-within:border-primary/35 focus-within:ring-3 focus-within:ring-primary/8">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleComposerKeyDown}
                disabled={sending}
                rows={1}
                placeholder="输入消息…"
                aria-label="输入聊天消息"
                className="max-h-40 min-h-12 w-full resize-none bg-transparent px-3 py-3 text-sm leading-6 outline-none placeholder:text-muted-foreground/65 disabled:opacity-60 sm:text-[15px]"
              />
              <div className="flex items-center justify-between gap-3 px-1 pb-1">
                <span className="hidden pl-2 text-[10px] text-muted-foreground sm:block">
                  Enter 发送 · Shift + Enter 换行
                </span>
                <div className="ml-auto flex items-center gap-2">
                  {sending && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => abortRef.current?.abort()}
                      className="rounded-xl text-xs"
                    >
                      <X className="size-3.5" />
                      停止
                    </Button>
                  )}
                  <Button
                    type="button"
                    size="icon"
                    onClick={() => void submitMessage()}
                    disabled={!input.trim() || sending}
                    className="rounded-xl shadow-sm shadow-primary/15"
                    aria-label="发送消息"
                  >
                    {sending ? <LoaderCircle className="size-4 animate-spin" /> : <SendHorizontal className="size-4" />}
                  </Button>
                </div>
              </div>
            </div>
            <p className="mt-2 text-center text-[10px] text-muted-foreground/75">
              AI 生成内容可能存在错误，请对重要信息进行核验。
            </p>
          </div>
        </footer>
      </section>
    </main>
  )
}
