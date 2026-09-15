"use client"

import * as React from "react"
import { Bot, CircleAlert, LoaderCircle, Sparkles, Square } from "lucide-react"

import type { UiMessage } from "@/components/chat/use-chat-workspace"
import { cn } from "@/lib/utils"

const suggestions = [
  "帮我梳理一个复杂问题的思路",
  "把这段想法整理成清晰的结构",
  "解释一个我正在学习的概念",
  "为下一步工作列出可执行方案",
]

type MessageThreadProps = {
  messages: UiMessage[]
  loading: boolean
  sending: boolean
  onSuggestion: (content: string) => void
}

export function MessageThread({
  messages,
  loading,
  sending,
  onSuggestion,
}: MessageThreadProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    const viewport = scrollRef.current
    if (!viewport) return
    viewport.scrollTo({
      top: viewport.scrollHeight,
      behavior: sending ? "auto" : "smooth",
    })
  }, [messages, sending])

  return (
    <div
      ref={scrollRef}
      className="min-h-0 flex-1 [scrollbar-width:thin] overflow-y-auto"
      aria-busy={loading || sending}
    >
      <div className="mx-auto flex min-h-full w-full max-w-4xl flex-col px-4 py-8 sm:px-8 sm:py-10">
        {loading ? (
          <div className="my-auto flex flex-col items-center gap-3 py-12 text-sm text-muted-foreground">
            <span className="grid size-11 place-items-center rounded-2xl bg-primary/10 text-primary">
              <LoaderCircle className="size-5 animate-spin" />
            </span>
            正在读取对话…
          </div>
        ) : messages.length === 0 ? (
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
              输入问题开始新对话。回答会实时生成，完成后自动保存到对话记录。
            </p>
            <div className="mt-8 grid w-full max-w-2xl gap-3 sm:grid-cols-2">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => onSuggestion(suggestion)}
                  className="rounded-2xl border bg-card/60 px-4 py-3.5 text-left text-sm leading-5 text-muted-foreground transition hover:-translate-y-0.5 hover:border-primary/25 hover:bg-card hover:text-foreground hover:shadow-sm"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-8 pb-8" role="log" aria-live="polite">
            {messages.map((message) => (
              <article
                key={message.id}
                className={cn(
                  "flex gap-3 sm:gap-4",
                  message.role === "user" && "justify-end"
                )}
              >
                {message.role === "assistant" && (
                  <span className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                    <Bot className="size-4" />
                  </span>
                )}
                <div
                  className={cn(
                    "max-w-[85%] min-w-0 text-sm leading-7 break-words whitespace-pre-wrap sm:max-w-[78%] sm:text-[15px]",
                    message.role === "user"
                      ? "rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-primary-foreground shadow-sm"
                      : "pt-0.5 text-foreground/90"
                  )}
                >
                  <div>
                    {message.content}
                    {message.status === "streaming" && (
                      <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded-full bg-primary align-middle" />
                    )}
                  </div>
                  {message.status === "interrupted" && (
                    <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border bg-muted/45 px-2.5 py-1 text-[10px] font-medium text-muted-foreground">
                      <Square className="size-2.5 fill-current" />{" "}
                      本次生成已停止
                    </div>
                  )}
                  {message.status === "failed" && (
                    <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-destructive/20 bg-destructive/5 px-2.5 py-1 text-[10px] font-medium text-destructive">
                      <CircleAlert className="size-3" /> 回答未完整生成
                    </div>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
