"use client"

import * as React from "react"
import { ArrowUp, BrainCircuit, Square, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type Props = {
  value: string
  sending: boolean
  error: string
  empty: boolean
  enableReasoning: boolean
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
  onChange: (value: string) => void
  onSend: () => void
  onStop: () => void
  onClearError: () => void
  onToggleReasoning: () => void
  onSuggestion: (value: string) => void
}
const suggestions = [
  "帮我梳理一个复杂问题",
  "解释一个我正在学习的概念",
  "为下一步工作制定计划",
]
export function ChatComposer({
  value,
  sending,
  error,
  empty,
  enableReasoning,
  textareaRef,
  onChange,
  onSend,
  onStop,
  onClearError,
  onToggleReasoning,
  onSuggestion,
}: Props) {
  React.useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return
    textarea.style.height = "0px"
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`
  }, [textareaRef, value])
  return (
    <footer
      className={cn(
        "w-full shrink-0 px-3 sm:px-6",
        empty ? "pt-8" : "bg-background pb-3 sm:pb-5"
      )}
    >
      <div className="mx-auto max-w-[800px]">
        {error && (
          <div
            role="alert"
            className="mb-2 flex items-center justify-between rounded-xl bg-destructive/10 px-3 py-2 text-xs text-destructive"
          >
            <span>{error}</span>
            <button aria-label="关闭错误" onClick={onClearError}>
              <X className="size-4" />
            </button>
          </div>
        )}
        <div className="rounded-[26px] border border-border bg-card p-2 shadow-[0_2px_18px_rgba(0,0,0,0.05)] focus-within:border-ring/50">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey &&
                !event.nativeEvent.isComposing
              ) {
                event.preventDefault()
                onSend()
              }
            }}
            disabled={sending}
            maxLength={20000}
            rows={1}
            placeholder="向 Agent Studio 提问"
            aria-label="输入聊天消息"
            className="max-h-[180px] min-h-[54px] w-full resize-none bg-transparent px-3 py-2.5 text-[15px] leading-7 outline-none placeholder:text-muted-foreground"
          />
          <div className="flex items-center justify-between px-1 pb-1">
            <Button
              type="button"
              variant={enableReasoning ? "secondary" : "ghost"}
              size="sm"
              className="rounded-full text-xs"
              onClick={onToggleReasoning}
              disabled={sending}
              aria-pressed={enableReasoning}
              title="后端支持开启或关闭推理"
            >
              <BrainCircuit className="size-4" /> 深度思考{" "}
              {enableReasoning ? "开" : "关"}
            </Button>
            {sending ? (
              <Button
                type="button"
                size="icon-sm"
                className="rounded-full"
                onClick={onStop}
                aria-label="停止生成"
              >
                <Square className="size-3.5 fill-current" />
              </Button>
            ) : (
              <Button
                type="button"
                size="icon-sm"
                className="rounded-full"
                onClick={onSend}
                disabled={!value.trim()}
                aria-label="发送消息"
              >
                <ArrowUp className="size-4" />
              </Button>
            )}
          </div>
        </div>
        {empty && (
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            {suggestions.map((item) => (
              <button
                key={item}
                onClick={() => onSuggestion(item)}
                className="rounded-full border px-3 py-2 text-xs text-muted-foreground transition hover:bg-muted hover:text-foreground"
              >
                {item}
              </button>
            ))}
          </div>
        )}
        <p className="mt-3 text-center text-[11px] text-muted-foreground">
          AI 可能会犯错，请核对重要信息。Enter 发送 · Shift + Enter 换行
        </p>
      </div>
    </footer>
  )
}
