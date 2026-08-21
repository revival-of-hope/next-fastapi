"use client"

import * as React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { ArrowLeft, ArrowRight, Bot, Eye, EyeOff, LoaderCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import { getApiErrorMessage, loginUser, registerUser } from "@/lib/api"
import { setAccessToken } from "@/lib/auth"
import { cn } from "@/lib/utils"

type AuthMode = "register" | "login"

export function AuthCard({ mode }: { mode: AuthMode }) {
  const router = useRouter()
  const isRegister = mode === "register"
  const [name, setName] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [confirmPassword, setConfirmPassword] = React.useState("")
  const [showPassword, setShowPassword] = React.useState(false)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState("")

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")

    const normalizedName = name.trim()
    if (!normalizedName) {
      setError("请输入用户名。")
      return
    }
    if (password.length < 8 || password.length > 16) {
      setError("密码长度应为 8–16 位。")
      return
    }
    if (isRegister && password !== confirmPassword) {
      setError("两次输入的密码不一致。")
      return
    }

    setLoading(true)
    try {
      if (isRegister) {
        await registerUser(normalizedName, password)
      }
      const token = await loginUser(normalizedName, password)
      setAccessToken(token.access_token)
      router.replace("/user/me/chat")
    } catch (err) {
      setError(
        getApiErrorMessage(
          err,
          isRegister ? "注册失败，请检查用户名后重试。" : "登录失败，请检查用户名和密码。",
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative grid min-h-svh place-items-center overflow-hidden bg-background px-5 py-10">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_-10%,color-mix(in_oklch,var(--primary)_18%,transparent),transparent_38%)]" />
      <div className="absolute top-5 left-5 sm:top-8 sm:left-8">
        <Button asChild variant="ghost" className="rounded-full">
          <Link href="/">
            <ArrowLeft className="size-4" />
            返回首页
          </Link>
        </Button>
      </div>
      <div className="absolute top-5 right-5 sm:top-8 sm:right-8">
        <ThemeToggle />
      </div>

      <section className="relative w-full max-w-md rounded-[1.75rem] border bg-card/90 p-6 shadow-2xl shadow-foreground/5 backdrop-blur-xl sm:p-8">
        <div className="mb-7">
          <div className="mb-5 grid size-11 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-sm shadow-primary/20">
            <Bot className="size-5" />
          </div>
          <h1 className="font-heading text-2xl font-semibold tracking-tight">
            {isRegister ? "创建你的账户" : "欢迎回来"}
          </h1>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {isRegister
              ? "完成注册后将自动登录并进入智能体对话页面。"
              : "登录后继续访问你的智能体与历史回复。"}
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">用户名</label>
            <input
              id="name"
              name="name"
              autoComplete="username"
              value={name}
              onChange={(event) => setName(event.target.value)}
              disabled={loading}
              placeholder="输入用户名"
              className="h-11 w-full rounded-xl border bg-background px-3.5 text-sm outline-none transition placeholder:text-muted-foreground/65 focus:border-primary/55 focus:ring-3 focus:ring-primary/10 disabled:opacity-60"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">密码</label>
            <div className="relative">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete={isRegister ? "new-password" : "current-password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={loading}
                placeholder="8–16 位密码"
                className="h-11 w-full rounded-xl border bg-background px-3.5 pr-11 text-sm outline-none transition placeholder:text-muted-foreground/65 focus:border-primary/55 focus:ring-3 focus:ring-primary/10 disabled:opacity-60"
              />
              <button
                type="button"
                aria-label={showPassword ? "隐藏密码" : "显示密码"}
                onClick={() => setShowPassword((value) => !value)}
                className="absolute top-1/2 right-3 grid size-7 -translate-y-1/2 place-items-center rounded-lg text-muted-foreground transition hover:bg-muted hover:text-foreground"
              >
                {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              </button>
            </div>
          </div>

          {isRegister && (
            <div className="space-y-2">
              <label htmlFor="confirm-password" className="text-sm font-medium">确认密码</label>
              <input
                id="confirm-password"
                name="confirm-password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                disabled={loading}
                placeholder="再次输入密码"
                className="h-11 w-full rounded-xl border bg-background px-3.5 text-sm outline-none transition placeholder:text-muted-foreground/65 focus:border-primary/55 focus:ring-3 focus:ring-primary/10 disabled:opacity-60"
              />
            </div>
          )}

          <div
            role="alert"
            aria-live="polite"
            className={cn(
              "overflow-hidden rounded-xl border px-3.5 text-sm leading-5 transition-all",
              error
                ? "max-h-24 border-destructive/20 bg-destructive/5 py-2.5 text-destructive opacity-100"
                : "max-h-0 border-transparent py-0 opacity-0",
            )}
          >
            {error || "占位"}
          </div>

          <Button type="submit" size="lg" className="h-11 w-full rounded-xl" disabled={loading}>
            {loading ? (
              <>
                <LoaderCircle className="size-4 animate-spin" />
                {isRegister ? "正在创建账户…" : "正在登录…"}
              </>
            ) : (
              <>
                {isRegister ? "注册并进入聊天" : "登录并进入聊天"}
                <ArrowRight className="size-4" />
              </>
            )}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          {isRegister ? "已有账户？" : "还没有账户？"}{" "}
          <Link
            href={isRegister ? "/user/login" : "/user/register"}
            className="font-medium text-foreground underline decoration-border underline-offset-4 transition hover:decoration-foreground"
          >
            {isRegister ? "直接登录" : "立即注册"}
          </Link>
        </p>
      </section>
    </main>
  )
}
