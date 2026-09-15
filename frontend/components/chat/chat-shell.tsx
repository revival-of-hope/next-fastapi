"use client"

import * as React from "react"
import {
  LoaderCircle,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react"

import { ChatComposer } from "@/components/chat/chat-composer"
import { ChatSidebar } from "@/components/chat/chat-sidebar"
import { MessageThread } from "@/components/chat/message-thread"
import { useChatWorkspace } from "@/components/chat/use-chat-workspace"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"

export function ChatShell() {
  const workspace = useChatWorkspace()
  const [input, setInput] = React.useState("")
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  function focusComposer() {
    window.setTimeout(() => textareaRef.current?.focus(), 0)
  }

  function startNewChat() {
    workspace.startNewChat()
    setInput("")
    setMobileSidebarOpen(false)
    focusComposer()
  }

  function selectConversation(conversationId: number) {
    setMobileSidebarOpen(false)
    void workspace.openConversation(conversationId)
  }

  function chooseSuggestion(content: string) {
    setInput(content)
    focusComposer()
  }

  async function sendMessage() {
    const content = input.trim()
    if (!content || workspace.sending) return

    setInput("")
    const accepted = await workspace.sendMessage(content)
    if (!accepted) setInput(content)
    focusComposer()
  }

  if (workspace.booting) {
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

  const activeTitle = workspace.activeConversation?.title?.trim() || "新对话"

  return (
    <main className="flex h-svh overflow-hidden bg-background">
      {mobileSidebarOpen && (
        <button
          type="button"
          aria-label="关闭侧栏"
          className="fixed inset-0 z-40 bg-black/35 backdrop-blur-[1px] lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      <ChatSidebar
        user={workspace.user}
        conversations={workspace.conversations}
        activeConversationId={workspace.activeConversationId}
        collapsed={sidebarCollapsed}
        mobileOpen={mobileSidebarOpen}
        loading={
          workspace.refreshingConversations &&
          workspace.conversations.length === 0
        }
        navigationDisabled={workspace.sending}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        onNewChat={startNewChat}
        onSelectConversation={selectConversation}
        onLogout={workspace.logout}
      />

      <section className="flex min-w-0 flex-1 flex-col bg-background">
        <header className="flex h-16 shrink-0 items-center justify-between border-b px-3 sm:px-5">
          <div className="flex min-w-0 items-center gap-1.5">
            <Button
              variant="ghost"
              size="icon"
              className="shrink-0 rounded-full lg:hidden"
              aria-label="打开侧栏"
              onClick={() => setMobileSidebarOpen(true)}
            >
              <Menu className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="hidden shrink-0 rounded-full lg:inline-flex"
              aria-label={sidebarCollapsed ? "展开侧栏" : "收起侧栏"}
              onClick={() => setSidebarCollapsed((value) => !value)}
            >
              {sidebarCollapsed ? (
                <PanelLeftOpen className="size-4" />
              ) : (
                <PanelLeftClose className="size-4" />
              )}
            </Button>
            <div className="ml-1 min-w-0">
              <div className="truncate font-heading text-sm font-semibold">
                {activeTitle}
              </div>
              <div className="hidden text-[11px] text-muted-foreground sm:block">
                {workspace.sending
                  ? "正在生成回复…"
                  : "实时流式回复 · 自动保存对话"}
              </div>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <ThemeToggle />
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full lg:hidden"
              onClick={workspace.logout}
              aria-label="退出登录"
            >
              <LogOut className="size-4" />
            </Button>
          </div>
        </header>

        <MessageThread
          messages={workspace.messages}
          loading={workspace.loadingMessages}
          sending={workspace.sending}
          onSuggestion={chooseSuggestion}
        />

        <ChatComposer
          value={input}
          sending={workspace.sending}
          error={workspace.error}
          textareaRef={textareaRef}
          onChange={setInput}
          onSend={() => void sendMessage()}
          onStop={workspace.stopGenerating}
          onClearError={workspace.clearError}
        />
      </section>
    </main>
  )
}
