import {
  Bot,
  Clock3,
  History,
  LoaderCircle,
  LogOut,
  MessageSquareText,
  Plus,
  UserRound,
  X,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import type { ConversationPublic, UserPublic } from "@/lib/api-types"
import { cn } from "@/lib/utils"

function conversationTitle(conversation: ConversationPublic): string {
  return conversation.title?.trim() || "新对话"
}

function formatConversationTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return "最近更新"

  const now = new Date()
  const sameDay = now.toDateString() === date.toDateString()
  return new Intl.DateTimeFormat("zh-CN", {
    ...(sameDay ? {} : { month: "numeric", day: "numeric" }),
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date)
}

type ChatSidebarProps = {
  user: UserPublic | null
  conversations: ConversationPublic[]
  activeConversationId: number | null
  collapsed: boolean
  mobileOpen: boolean
  loading: boolean
  navigationDisabled: boolean
  onCloseMobile: () => void
  onNewChat: () => void
  onSelectConversation: (conversationId: number) => void
  onLogout: () => void
}

export function ChatSidebar({
  user,
  conversations,
  activeConversationId,
  collapsed,
  mobileOpen,
  loading,
  navigationDisabled,
  onCloseMobile,
  onNewChat,
  onSelectConversation,
  onLogout,
}: ChatSidebarProps) {
  return (
    <aside
      aria-label="对话侧栏"
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex w-[288px] flex-col border-r bg-sidebar transition-[width,transform] duration-200 lg:relative lg:z-auto lg:shrink-0",
        mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        collapsed ? "lg:w-[76px]" : "lg:w-[288px]"
      )}
    >
      <div className="flex h-16 shrink-0 items-center justify-between px-3.5">
        <div
          className={cn(
            "flex min-w-0 items-center gap-2.5",
            collapsed && "lg:w-full lg:justify-center"
          )}
        >
          <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm shadow-primary/20">
            <Bot className="size-5" />
          </span>
          <div className={cn("min-w-0", collapsed && "lg:hidden")}>
            <div className="truncate font-heading text-sm font-semibold">
              Agent Studio
            </div>
            <div className="truncate text-[11px] text-muted-foreground">
              AI workspace
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="关闭侧栏"
          onClick={onCloseMobile}
          className="lg:hidden"
        >
          <X className="size-4" />
        </Button>
      </div>

      <div className="px-3 pb-3">
        <Button
          variant="outline"
          className={cn(
            "h-10 w-full justify-start rounded-xl bg-background/70 shadow-none",
            collapsed && "lg:justify-center lg:px-0"
          )}
          onClick={onNewChat}
          disabled={navigationDisabled}
          title={collapsed ? "新对话" : undefined}
        >
          <Plus className="size-4" />
          <span className={cn(collapsed && "lg:hidden")}>新对话</span>
        </Button>
      </div>

      <div
        className={cn(
          "flex items-center gap-2 px-4 pb-2 text-[11px] font-medium tracking-wide text-muted-foreground uppercase",
          collapsed && "lg:justify-center lg:px-2"
        )}
      >
        <History className="size-3.5" />
        <span className={cn(collapsed && "lg:hidden")}>对话记录</span>
      </div>

      <div className="min-h-0 flex-1 [scrollbar-width:thin] overflow-y-auto px-2.5 pb-3">
        {loading ? (
          <div className="grid place-items-center py-8 text-muted-foreground">
            <LoaderCircle className="size-4 animate-spin" />
          </div>
        ) : conversations.length === 0 ? (
          <div
            className={cn(
              "mx-1 rounded-xl border border-dashed px-3 py-5 text-center text-xs leading-5 text-muted-foreground",
              collapsed && "lg:hidden"
            )}
          >
            暂无对话。发送第一条消息后会自动创建。
          </div>
        ) : (
          <nav aria-label="历史对话" className="space-y-1">
            {conversations.map((conversation) => {
              const selected =
                conversation.conversation_id === activeConversationId
              const title = conversationTitle(conversation)

              return (
                <button
                  key={conversation.conversation_id}
                  type="button"
                  title={collapsed ? title : undefined}
                  aria-current={selected ? "page" : undefined}
                  disabled={navigationDisabled}
                  onClick={() =>
                    onSelectConversation(conversation.conversation_id)
                  }
                  className={cn(
                    "group flex w-full items-start gap-2.5 rounded-xl px-2.5 py-2.5 text-left text-sm transition disabled:cursor-not-allowed disabled:opacity-60",
                    selected
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "hover:bg-sidebar-accent/70",
                    collapsed && "lg:justify-center lg:px-2"
                  )}
                >
                  <MessageSquareText
                    className={cn(
                      "mt-0.5 size-4 shrink-0 text-muted-foreground transition group-hover:text-foreground",
                      selected && "text-primary"
                    )}
                  />
                  <span
                    className={cn("min-w-0 flex-1", collapsed && "lg:hidden")}
                  >
                    <span className="block truncate text-[13px] font-medium text-sidebar-foreground/90">
                      {title}
                    </span>
                    <span className="mt-0.5 flex items-center gap-1 text-[10px] text-muted-foreground">
                      <Clock3 className="size-2.5" />
                      {formatConversationTime(conversation.updated_at)}
                    </span>
                  </span>
                </button>
              )
            })}
          </nav>
        )}
      </div>

      <div className="border-t p-3">
        <div
          className={cn(
            "flex items-center gap-2.5 rounded-xl px-2 py-2",
            collapsed && "lg:justify-center lg:px-0"
          )}
        >
          <span className="grid size-8 shrink-0 place-items-center rounded-full bg-primary/10 text-primary">
            <UserRound className="size-4" />
          </span>
          <div className={cn("min-w-0 flex-1", collapsed && "lg:hidden")}>
            <div className="truncate text-xs font-medium">
              {user?.name || "用户"}
            </div>
            <div className="text-[10px] text-muted-foreground">已登录</div>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="退出登录"
            title="退出登录"
            onClick={onLogout}
            className={cn(collapsed && "lg:hidden")}
          >
            <LogOut className="size-3.5" />
          </Button>
        </div>
      </div>
    </aside>
  )
}
