"use client"

import * as React from "react"
import Link from "next/link"
import {
  ArrowDown,
  LogOut,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  PenLine,
  Search,
  Shield,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import type { ConversationPublic, UserPublic } from "@/lib/api-types"
import { cn } from "@/lib/utils"

type Props = {
  user: UserPublic | null
  conversations: ConversationPublic[]
  activeConversationId: number | null
  collapsed: boolean
  mobileOpen: boolean
  loading: boolean
  navigationDisabled: boolean
  hasMore: boolean
  onLoadMore: () => void
  onToggleCollapsed: () => void
  onCloseMobile: () => void
  onNewChat: () => void
  onSelectConversation: (id: number) => void
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
  hasMore,
  onLoadMore,
  onToggleCollapsed,
  onCloseMobile,
  onNewChat,
  onSelectConversation,
  onLogout,
}: Props) {
  const [searchOpen, setSearchOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")
  const filtered = conversations.filter((item) =>
    (item.title || "新对话").toLowerCase().includes(search.toLowerCase())
  )
  return (
    <aside
      aria-label="对话侧栏"
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col bg-sidebar text-sidebar-foreground transition-[width,transform] duration-200 lg:relative lg:z-auto lg:shrink-0",
        mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        collapsed ? "lg:w-[68px]" : "lg:w-[280px]"
      )}
    >
      <div className="flex h-16 shrink-0 items-center justify-between gap-2 px-4">
        <Link
          href="/user/me/chat"
          className={cn(
            "truncate text-[19px] font-semibold tracking-tight",
            collapsed && "lg:hidden"
          )}
          onClick={onCloseMobile}
        >
          Agent Studio
        </Link>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={collapsed ? "展开侧栏" : "收起侧栏"}
            onClick={onToggleCollapsed}
            className="hidden lg:inline-flex"
          >
            {collapsed ? (
              <PanelLeftOpen className="size-4" />
            ) : (
              <PanelLeftClose className="size-4" />
            )}
          </Button>
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
      </div>
      <div className="space-y-1 px-2.5 pt-2">
        <Button
          variant="ghost"
          className={cn(
            "h-11 w-full justify-start gap-3 rounded-xl px-3 text-[14px] font-normal",
            collapsed && "lg:justify-center lg:px-0"
          )}
          onClick={onNewChat}
          disabled={navigationDisabled}
          title="新聊天"
        >
          <PenLine className="size-[18px]" />
          <span className={cn(collapsed && "lg:hidden")}>新聊天</span>
        </Button>
        <Button
          variant="ghost"
          className={cn(
            "h-11 w-full justify-start gap-3 rounded-xl px-3 text-[14px] font-normal",
            collapsed && "lg:justify-center lg:px-0"
          )}
          onClick={() => {
            setSearchOpen((value) => !value)
            if (collapsed) onToggleCollapsed()
          }}
          title="搜索聊天"
        >
          <Search className="size-[18px]" />
          <span className={cn(collapsed && "lg:hidden")}>搜索聊天</span>
        </Button>
        {searchOpen && (
          <input
            autoFocus
            aria-label="按标题搜索已加载的对话"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="搜索已加载的对话…"
            className={cn(
              "mb-2 h-9 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring/40",
              collapsed && "lg:hidden"
            )}
          />
        )}
      </div>
      <div
        className={cn(
          "mt-7 px-5 pb-2 text-xs font-medium text-muted-foreground",
          collapsed && "lg:hidden"
        )}
      >
        最近
      </div>
      <nav
        aria-label="历史对话"
        className="min-h-0 flex-1 [scrollbar-width:thin] overflow-y-auto px-2.5 pb-4"
      >
        {filtered.map((item) => (
          <button
            key={item.conversation_id}
            type="button"
            disabled={navigationDisabled}
            title={item.title || "新对话"}
            aria-current={
              item.conversation_id === activeConversationId ? "page" : undefined
            }
            onClick={() => onSelectConversation(item.conversation_id)}
            className={cn(
              "mb-0.5 flex h-10 w-full items-center gap-2.5 rounded-xl px-3 text-left text-[13px] transition hover:bg-sidebar-accent disabled:opacity-50",
              item.conversation_id === activeConversationId &&
                "bg-sidebar-accent font-medium",
              collapsed && "lg:justify-center lg:px-0"
            )}
          >
            <MessageSquare
              className={cn(
                "size-4 shrink-0 lg:hidden",
                collapsed && "lg:block"
              )}
            />
            <span className={cn("truncate", collapsed && "lg:hidden")}>
              {item.title?.trim() || "新对话"}
            </span>
          </button>
        ))}
        {!filtered.length && (
          <p
            className={cn(
              "px-3 py-4 text-xs leading-5 text-muted-foreground",
              collapsed && "lg:hidden"
            )}
          >
            {search ? "没有匹配的对话" : "发送消息后，对话会显示在这里。"}
          </p>
        )}
        {hasMore && !search && (
          <Button
            variant="ghost"
            className={cn(
              "w-full justify-start text-xs text-muted-foreground",
              collapsed && "lg:hidden"
            )}
            onClick={onLoadMore}
            disabled={loading}
          >
            <ArrowDown className="size-3.5" />
            {loading ? "加载中…" : "加载更多对话"}
          </Button>
        )}
      </nav>
      <div className="border-t border-sidebar-border/70 p-2.5">
        {user?.is_superuser && (
          <Button
            asChild
            variant="ghost"
            className={cn(
              "mb-1 w-full justify-start gap-3 rounded-xl text-xs",
              collapsed && "lg:justify-center lg:px-0"
            )}
            title="管理后台"
          >
            <Link href="/user/me/admin">
              <Shield className="size-4" />
              <span className={cn(collapsed && "lg:hidden")}>管理后台</span>
            </Link>
          </Button>
        )}
        <div
          className={cn(
            "flex items-center gap-2 rounded-xl px-2 py-1",
            collapsed && "lg:justify-center lg:px-0"
          )}
        >
          <span className="grid size-8 shrink-0 place-items-center rounded-full bg-[#d9c9ad] text-xs font-semibold text-[#594b36]">
            {user?.name?.slice(0, 1).toUpperCase() || "U"}
          </span>
          <span
            className={cn(
              "min-w-0 flex-1 truncate text-xs",
              collapsed && "lg:hidden"
            )}
          >
            {user?.name || "用户"}
            {user?.usage && (
              <span className="block text-[10px] text-muted-foreground">
                已完成 {user.usage.messages_count} 次回答
              </span>
            )}
          </span>
          <span className={cn(collapsed && "lg:hidden")}>
            <ThemeToggle />
          </span>
        </div>
        <Button
          variant="ghost"
          className={cn(
            "mt-1 w-full justify-start gap-3 rounded-xl text-xs text-muted-foreground",
            collapsed && "lg:justify-center lg:px-0"
          )}
          onClick={onLogout}
          title="退出登录"
        >
          <LogOut className="size-4" />
          <span className={cn(collapsed && "lg:hidden")}>退出登录</span>
        </Button>
      </div>
    </aside>
  )
}
