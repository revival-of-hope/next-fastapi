"use client"

import * as React from "react"
import { LoaderCircle, Menu } from "lucide-react"
import { ChatComposer } from "@/components/chat/chat-composer"
import { ChatSidebar } from "@/components/chat/chat-sidebar"
import { MessageThread } from "@/components/chat/message-thread"
import { useChatWorkspace } from "@/components/chat/use-chat-workspace"
import { Button } from "@/components/ui/button"

export function ChatShell() {
  const workspace = useChatWorkspace()
  const [input, setInput] = React.useState("")
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)
  const empty = !workspace.loadingMessages && workspace.messages.length === 0
  function focusComposer() {
    window.setTimeout(() => textareaRef.current?.focus(), 0)
  }
  function startNewChat() {
    workspace.startNewChat()
    setInput("")
    setMobileSidebarOpen(false)
    focusComposer()
  }
  function chooseSuggestion(content: string) {
    setInput(content)
    focusComposer()
  }
  async function sendMessage() {
    const content = input.trim()
    if (!content || workspace.sending) return
    setInput("")
    if (!(await workspace.sendMessage(content))) setInput(content)
    focusComposer()
  }
  if (workspace.booting)
    return (
      <main className="grid h-svh place-items-center text-sm text-muted-foreground">
        <LoaderCircle className="size-5 animate-spin" />
        正在加载…
      </main>
    )
  return (
    <main className="flex h-svh overflow-hidden bg-background">
      {mobileSidebarOpen && (
        <button
          type="button"
          aria-label="关闭侧栏"
          onClick={() => setMobileSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/35 lg:hidden"
        />
      )}
      <ChatSidebar
        user={workspace.user}
        conversations={workspace.conversations}
        activeConversationId={workspace.activeConversationId}
        collapsed={sidebarCollapsed}
        mobileOpen={mobileSidebarOpen}
        loading={workspace.refreshingConversations}
        navigationDisabled={workspace.sending}
        hasMore={workspace.hasMoreConversations}
        onLoadMore={() => void workspace.loadMoreConversations()}
        onToggleCollapsed={() => setSidebarCollapsed((value) => !value)}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        onNewChat={startNewChat}
        onSelectConversation={(id) => {
          setMobileSidebarOpen(false)
          void workspace.openConversation(id)
        }}
        onLogout={workspace.logout}
      />
      <section className="flex min-w-0 flex-1 flex-col bg-background">
        <header className="flex h-16 shrink-0 items-center px-3 sm:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="mr-2 lg:hidden"
            aria-label="打开侧栏"
            onClick={() => setMobileSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </Button>
          <span className="max-w-[50vw] truncate text-[16px] font-semibold tracking-tight">
            Agent Studio
          </span>
          <span className="ml-2 hidden text-xs text-muted-foreground sm:inline">
            {workspace.activeConversation?.title || "聊天"}
          </span>
        </header>
        <div
          className={
            empty
              ? "flex min-h-0 flex-1 flex-col justify-center pb-[8vh]"
              : "flex min-h-0 flex-1 flex-col"
          }
        >
          <MessageThread
            messages={workspace.messages}
            loading={workspace.loadingMessages}
            sending={workspace.sending}
          />
          <ChatComposer
            value={input}
            sending={workspace.sending}
            error={workspace.error}
            empty={empty}
            enableReasoning={workspace.enableReasoning}
            textareaRef={textareaRef}
            onChange={setInput}
            onSend={() => void sendMessage()}
            onStop={workspace.stopGenerating}
            onClearError={workspace.clearError}
            onToggleReasoning={() =>
              workspace.setEnableReasoning((value) => !value)
            }
            onSuggestion={chooseSuggestion}
          />
        </div>
      </section>
    </main>
  )
}
