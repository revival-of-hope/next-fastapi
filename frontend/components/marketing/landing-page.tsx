"use client"

import Link from "next/link"
import {
  ArrowRight,
  Bot,
  Braces,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"

const features = [
  {
    icon: Zap,
    title: "实时流式回复",
    description: "FastAPI 流式响应与前端逐字呈现，让对话反馈更自然。",
  },
  {
    icon: MessageSquareText,
    title: "历史记录",
    description: "登录后自动读取你的历史回复，最近内容随时可回看。",
  },
  {
    icon: ShieldCheck,
    title: "Token 鉴权",
    description: "注册后自动登录，后续用户接口统一携带 Bearer Token。",
  },
]

export function LandingPage() {
  return (
    <main className="relative min-h-svh overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,color-mix(in_oklch,var(--primary)_15%,transparent),transparent_30%),radial-gradient(circle_at_80%_10%,color-mix(in_oklch,var(--chart-2)_10%,transparent),transparent_26%)]" />
      <div className="pointer-events-none absolute inset-0 opacity-[0.035] [background-image:linear-gradient(to_right,currentColor_1px,transparent_1px),linear-gradient(to_bottom,currentColor_1px,transparent_1px)] [background-size:42px_42px]" />

      <div className="relative mx-auto flex min-h-svh max-w-7xl flex-col px-5 sm:px-8 lg:px-10">
        <header className="flex h-20 items-center justify-between border-b border-border/60">
          <Link href="/" className="flex items-center gap-2.5" aria-label="智能体首页">
            <span className="grid size-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm shadow-primary/20">
              <Bot className="size-5" />
            </span>
            <span className="font-heading text-lg font-semibold tracking-tight">Agent Studio</span>
          </Link>
          <div className="flex items-center gap-1 sm:gap-2">
            <ThemeToggle />
            <Button asChild variant="ghost" className="rounded-full px-4">
              <Link href="/user/login">登录</Link>
            </Button>
            <Button asChild className="rounded-full px-5 shadow-sm shadow-primary/20">
              <Link href="/user/register">
                注册
                <ArrowRight className="size-4" />
              </Link>
            </Button>
          </div>
        </header>

        <section className="grid flex-1 items-center gap-14 py-16 lg:grid-cols-[1.05fr_.95fr] lg:py-20">
          <div className="max-w-3xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-card/70 px-3 py-1.5 text-xs font-medium text-muted-foreground shadow-sm backdrop-blur">
              <Sparkles className="size-3.5 text-primary" />
              Next.js · FastAPI · AI Agent
            </div>
            <h1 className="font-heading text-5xl font-semibold tracking-[-0.045em] text-balance sm:text-6xl lg:text-7xl lg:leading-[1.02]">
              一个更专注的
              <span className="block text-primary">智能体工作空间</span>
            </h1>
            <p className="mt-7 max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg">
              从注册到对话保持在顺畅的单页体验中。无需复杂配置，创建账户后即可进入专属聊天空间，持续获得流式回答并回看历史内容。
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg" className="h-12 rounded-xl px-6 text-base shadow-lg shadow-primary/15">
                <Link href="/user/register">
                  创建账户并开始
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-12 rounded-xl px-6 text-base">
                <Link href="/user/login">已有账户，直接登录</Link>
              </Button>
            </div>
            <div className="mt-10 flex flex-wrap gap-x-6 gap-y-3 text-sm text-muted-foreground">
              <span className="flex items-center gap-2"><Braces className="size-4 text-primary" />Typed API client</span>
              <span className="flex items-center gap-2"><ShieldCheck className="size-4 text-primary" />Bearer authentication</span>
              <span className="flex items-center gap-2"><Zap className="size-4 text-primary" />Streaming response</span>
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-xl lg:mx-0 lg:ml-auto">
            <div className="absolute -inset-8 -z-10 rounded-[3rem] bg-primary/8 blur-3xl" />
            <div className="overflow-hidden rounded-[2rem] border bg-card/80 shadow-2xl shadow-foreground/5 backdrop-blur-xl">
              <div className="flex items-center gap-2 border-b px-5 py-4">
                <span className="size-2.5 rounded-full bg-foreground/15" />
                <span className="size-2.5 rounded-full bg-foreground/10" />
                <span className="size-2.5 rounded-full bg-foreground/10" />
                <span className="ml-2 text-xs text-muted-foreground">agent / conversation</span>
              </div>
              <div className="space-y-5 p-5 sm:p-7">
                <div className="ml-auto max-w-[78%] rounded-2xl rounded-br-md bg-primary px-4 py-3 text-sm leading-6 text-primary-foreground shadow-sm">
                  帮我梳理一下今天最重要的工作，并给出执行顺序。
                </div>
                <div className="flex max-w-[90%] gap-3">
                  <span className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-xl border bg-background">
                    <Bot className="size-4 text-primary" />
                  </span>
                  <div className="rounded-2xl rounded-tl-md border bg-background/80 px-4 py-3 text-sm leading-6 text-foreground/85">
                    可以。先处理有明确截止时间的任务，再安排需要连续专注的深度工作，最后集中处理低认知负荷的沟通与整理事项……
                    <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded-full bg-primary align-middle" />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3 pt-2">
                  {[
                    ["01", "创建账户"],
                    ["02", "自动登录"],
                    ["03", "开始对话"],
                  ].map(([number, label]) => (
                    <div key={number} className="rounded-2xl border bg-muted/45 p-3.5">
                      <div className="text-[11px] font-semibold text-primary">{number}</div>
                      <div className="mt-1 text-xs font-medium sm:text-sm">{label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 border-t border-border/60 py-8 md:grid-cols-3">
          {features.map(({ icon: Icon, title, description }) => (
            <div key={title} className="group rounded-2xl border border-transparent p-4 transition-colors hover:border-border hover:bg-card/70">
              <div className="mb-3 grid size-9 place-items-center rounded-xl bg-primary/10 text-primary">
                <Icon className="size-4.5" />
              </div>
              <h2 className="font-heading font-semibold">{title}</h2>
              <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{description}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  )
}
