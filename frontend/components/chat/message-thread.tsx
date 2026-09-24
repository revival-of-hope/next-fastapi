"use client"

import * as React from "react"
import { CircleAlert, LoaderCircle, Square } from "lucide-react"
import type { UiMessage } from "@/components/chat/use-chat-workspace"
import { cn } from "@/lib/utils"

type Props = { messages: UiMessage[]; loading: boolean; sending: boolean }
export function MessageThread({ messages, loading, sending }: Props) {
  const scrollRef = React.useRef<HTMLDivElement>(null)
  React.useEffect(() => {
    const viewport = scrollRef.current
    if (viewport && messages.length)
      viewport.scrollTo({
        top: viewport.scrollHeight,
        behavior: sending ? "instant" : "smooth",
      })
  }, [messages, sending])
  if (!loading && messages.length === 0)
    return (
      <div className="mx-auto w-full max-w-[800px] px-4 text-center sm:px-6">
        <h1 className="text-[25px] font-medium tracking-tight sm:text-[29px]">
          我们该做什么？
        </h1>
      </div>
    )
  return (
    <div
      ref={scrollRef}
      className="min-h-0 flex-1 [scrollbar-width:thin] overflow-y-auto"
      aria-busy={loading || sending}
    >
      <div className="mx-auto w-full max-w-[800px] px-4 py-8 sm:px-6 sm:py-12">
        {loading ? (
          <div className="flex items-center justify-center gap-2 py-20 text-sm text-muted-foreground">
            <LoaderCircle className="size-4 animate-spin" />
            正在读取对话…
          </div>
        ) : (
          <div className="space-y-8 pb-8" role="log" aria-live="polite">
            {messages.map((message) => (
              <article
                key={message.id}
                className={cn("flex", message.role === "user" && "justify-end")}
              >
                <div
                  className={cn(
                    "max-w-full min-w-0 text-[15px] leading-7 break-words whitespace-pre-wrap",
                    message.role === "user"
                      ? "max-w-[85%] rounded-3xl bg-muted px-4 py-2.5"
                      : "w-full px-1"
                  )}
                >
                  {message.role === "assistant" && message.reasoning && (
                    <details className="mb-4 rounded-xl bg-muted/60 p-3 text-sm text-muted-foreground">
                      <summary className="cursor-pointer">查看思考过程</summary>
                      <div className="mt-2 whitespace-pre-wrap">
                        {message.reasoning}
                      </div>
                    </details>
                  )}
                  {message.content}
                  {message.status === "streaming" && (
                    <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-foreground/60 align-middle" />
                  )}
                  {message.status === "interrupted" && (
                    <span className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                      <Square className="size-2.5 fill-current" />
                      已停止生成
                    </span>
                  )}
                  {message.status === "failed" && (
                    <span className="mt-2 flex items-center gap-1 text-xs text-destructive">
                      <CircleAlert className="size-3" />
                      回答未完整生成
                    </span>
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
