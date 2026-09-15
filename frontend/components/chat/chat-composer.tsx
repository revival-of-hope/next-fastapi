"use client"

import * as React from "react"
import { LoaderCircle, SendHorizontal, X } from "lucide-react"

import { Button } from "@/components/ui/button"

type ChatComposerProps = {
  value: string
  sending: boolean
  error: string
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
  onChange: (value: string) => void
  onSend: () => void
  onStop: () => void
  onClearError: () => void
}

export function ChatComposer({
  value,
  sending,
  error,
  textareaRef,
  onChange,
  onSend,
  onStop,
  onClearError,
}: ChatComposerProps) {
  React.useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return
    textarea.style.height = "0px"
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`
  }, [textareaRef, value])

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault()
      onSend()
    }
  }

  return (
    <footer className="shrink-0 bg-gradient-to-t from-background via-background to-background/0 px-3 pt-2 pb-3 sm:px-6 sm:pb-5">
      <div className="mx-auto max-w-4xl">
        {error && (
          <div
            role="alert"
            className="mb-2 flex items-center justify-between gap-3 rounded-xl border border-destructive/20 bg-destructive/5 px-3 py-2 text-xs text-destructive"
          >
            <span>{error}</span>
            <button
              type="button"
              onClick={onClearError}
              className="shrink-0 rounded-md p-1 hover:bg-destructive/10"
              aria-label="关闭错误提示"
            >
              <X className="size-3.5" />
            </button>
          </div>
        )}
        <div className="rounded-[1.4rem] border bg-card p-2 shadow-[0_10px_40px_-18px_color-mix(in_oklch,var(--foreground)_22%,transparent)] transition focus-within:border-primary/35 focus-within:ring-3 focus-within:ring-primary/8">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={sending}
            maxLength={20_000}
            rows={1}
            placeholder="输入消息…"
            aria-label="输入聊天消息"
            className="max-h-40 min-h-12 w-full resize-none bg-transparent px-3 py-3 text-sm leading-6 outline-none placeholder:text-muted-foreground/65 disabled:opacity-60 sm:text-[15px]"
          />
          <div className="flex items-center justify-between gap-3 px-1 pb-1">
            <span className="hidden pl-2 text-[10px] text-muted-foreground sm:block">
              {value.length >= 18_000
                ? `${value.length.toLocaleString()} / 20,000`
                : "Enter 发送 · Shift + Enter 换行"}
            </span>
            <div className="ml-auto flex items-center gap-2">
              {sending && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={onStop}
                  className="rounded-xl text-xs"
                >
                  <X className="size-3.5" />
                  停止
                </Button>
              )}
              <Button
                type="button"
                size="icon"
                onClick={onSend}
                disabled={!value.trim() || sending}
                className="rounded-xl shadow-sm shadow-primary/15"
                aria-label="发送消息"
              >
                {sending ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  <SendHorizontal className="size-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
        <p className="mt-2 text-center text-[10px] text-muted-foreground/75">
          AI 生成内容可能存在错误，请对重要信息进行核验。
        </p>
      </div>
    </footer>
  )
}
