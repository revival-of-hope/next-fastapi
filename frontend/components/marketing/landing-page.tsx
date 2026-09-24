import Link from "next/link"
import {
  ArrowRight,
  MessageSquareText,
  PanelLeft,
  Sparkles,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"

export function LandingPage() {
  return (
    <main className="min-h-svh bg-background">
      <header className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8">
        <Link href="/" className="text-xl font-semibold tracking-tight">
          Agent Studio
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button asChild variant="ghost">
            <Link href="/user/login">登录</Link>
          </Button>
          <Button asChild className="rounded-full px-5">
            <Link href="/user/register">
              注册 <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </header>
      <section className="mx-auto grid min-h-[calc(100svh-5rem)] max-w-7xl items-center gap-14 px-5 py-16 sm:px-8 lg:grid-cols-2">
        <div>
          <p className="mb-5 inline-flex items-center gap-2 text-sm text-muted-foreground">
            <Sparkles className="size-4" /> 一个简单、专注的对话空间
          </p>
          <h1 className="max-w-xl text-5xl leading-[1.15] font-medium tracking-tight sm:text-6xl">
            把想法说出来，
            <br />
            从这里开始。
          </h1>
          <p className="mt-6 max-w-lg text-base leading-8 text-muted-foreground">
            流式回答、历史对话与可选的深度思考，放在一个安静的工作界面里。
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Button asChild size="lg" className="rounded-full px-6">
              <Link href="/user/register">
                开始使用 <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="rounded-full px-6"
            >
              <Link href="/user/login">已有账号</Link>
            </Button>
          </div>
        </div>
        <div
          aria-hidden="true"
          className="overflow-hidden rounded-[28px] border bg-card shadow-[0_30px_80px_rgba(0,0,0,0.07)]"
        >
          <div className="flex min-h-[410px]">
            <div className="w-1/3 border-r bg-sidebar p-4">
              <p className="mb-8 text-sm font-semibold">Agent Studio</p>
              <p className="flex items-center gap-2 rounded-lg bg-muted px-2 py-2 text-xs">
                <MessageSquareText className="size-3.5" /> 新聊天
              </p>
              <p className="mt-5 text-xs text-muted-foreground">最近</p>
              <p className="mt-3 truncate text-xs">今天的思路整理</p>
            </div>
            <div className="flex flex-1 flex-col items-center justify-center gap-8 px-5">
              <PanelLeft className="size-4 self-start text-muted-foreground" />
              <p className="mt-auto text-center text-xl font-medium">
                我们该做什么？
              </p>
              <div className="w-full rounded-2xl border p-4 text-sm text-muted-foreground shadow-sm">
                向 Agent Studio 提问…{" "}
                <span className="float-right inline-flex size-6 items-center justify-center rounded-full bg-foreground text-background">
                  <ArrowRight className="size-3" />
                </span>
              </div>
              <div className="mb-auto" />
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
