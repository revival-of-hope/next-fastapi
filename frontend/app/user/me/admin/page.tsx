"use client"

import * as React from "react"
import Link from "next/link"
import { ArrowLeft, LoaderCircle, RefreshCw, Trash2, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  ApiError,
  deleteUser,
  getApiErrorMessage,
  getCurrentUser,
  getUsage,
  getUsers,
} from "@/lib/api"
import { getAccessToken } from "@/lib/auth"
import type { UsagePublic, UserPublic } from "@/lib/api-types"

export default function AdminPage() {
  const [users, setUsers] = React.useState<UserPublic[]>([])
  const [count, setCount] = React.useState(0)
  const [usage, setUsage] = React.useState<UsagePublic | null>(null)
  const [me, setMe] = React.useState<UserPublic | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [busy, setBusy] = React.useState(false)
  const [error, setError] = React.useState("")
  const [offset, setOffset] = React.useState(0)
  const token = React.useMemo(() => getAccessToken(), [])
  const load = React.useCallback(
    async (skip: number) => {
      if (!token) {
        setError("请先登录。")
        setLoading(false)
        return
      }
      setBusy(true)
      setError("")
      try {
        const current = await getCurrentUser(token)
        setMe(current)
        if (!current.is_superuser)
          throw new ApiError("当前账号没有管理员权限。", 403)
        const [page, totals] = await Promise.all([
          getUsers(token, skip, 50),
          getUsage(token),
        ])
        setUsers(page.data)
        setCount(page.count)
        setUsage(totals)
        setOffset(skip)
      } catch (err) {
        setError(getApiErrorMessage(err))
      } finally {
        setBusy(false)
        setLoading(false)
      }
    },
    [token]
  )
  React.useEffect(() => {
    const handle = window.setTimeout(() => {
      void load(0)
    }, 0)
    return () => window.clearTimeout(handle)
  }, [load])
  async function remove(user: UserPublic) {
    if (
      !token ||
      !window.confirm(
        `确定删除用户“${user.name}”及其全部对话吗？此操作无法撤销。`
      )
    )
      return
    setBusy(true)
    setError("")
    try {
      await deleteUser(token, user.user_id)
      await load(
        offset >= count - 1 && offset > 0 ? Math.max(0, offset - 50) : offset
      )
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }
  return (
    <main className="min-h-svh bg-background px-4 py-6 sm:px-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-10 flex items-center justify-between">
          <Button asChild variant="ghost">
            <Link href="/user/me/chat">
              <ArrowLeft className="size-4" /> 返回聊天
            </Link>
          </Button>
          <span className="text-sm font-medium">Agent Studio · 管理后台</span>
        </header>
        <h1 className="text-3xl font-semibold tracking-tight">用户管理</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          仅管理员可查看全站使用量与用户列表。
        </p>
        {error && (
          <p
            role="alert"
            className="mt-6 rounded-xl bg-destructive/10 p-4 text-sm text-destructive"
          >
            {error}
          </p>
        )}
        {loading ? (
          <p className="mt-12 flex gap-2 text-sm text-muted-foreground">
            <LoaderCircle className="size-4 animate-spin" />
            加载中…
          </p>
        ) : (
          me?.is_superuser && (
            <>
              <div className="my-8 grid gap-3 sm:grid-cols-4">
                {(
                  [
                    ["用户总数", count],
                    ["回答次数", usage?.messages_count],
                    ["输入 tokens", usage?.input_tokens],
                    ["输出 tokens", usage?.output_tokens],
                  ] as const
                ).map(([label, value]) => (
                  <div key={label} className="rounded-2xl border bg-card p-5">
                    <p className="text-xs text-muted-foreground">{label}</p>
                    <p className="mt-2 text-2xl font-semibold">
                      {value?.toLocaleString() ?? "—"}
                    </p>
                  </div>
                ))}
              </div>
              <div className="overflow-hidden rounded-2xl border">
                <div className="flex items-center justify-between border-b p-4">
                  <span className="flex items-center gap-2 text-sm font-medium">
                    <Users className="size-4" />
                    用户列表
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={busy}
                    onClick={() => void load(offset)}
                  >
                    <RefreshCw className="size-4" />
                    刷新
                  </Button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[650px] text-left text-sm">
                    <thead className="bg-muted/50 text-xs text-muted-foreground">
                      <tr>
                        <th className="px-4 py-3">用户名</th>
                        <th className="px-4 py-3">角色</th>
                        <th className="px-4 py-3">回答次数</th>
                        <th className="px-4 py-3">总 tokens</th>
                        <th className="px-4 py-3">创建时间</th>
                        <th className="px-4 py-3">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.user_id} className="border-t">
                          <td className="px-4 py-3 font-medium">{user.name}</td>
                          <td className="px-4 py-3">
                            {user.is_superuser
                              ? "管理员"
                              : user.is_active
                                ? "普通用户"
                                : "已停用"}
                          </td>
                          <td className="px-4 py-3">
                            {user.usage?.messages_count ?? 0}
                          </td>
                          <td className="px-4 py-3">
                            {user.usage?.total_tokens ?? 0}
                          </td>
                          <td className="px-4 py-3">
                            {new Date(user.created_at).toLocaleDateString(
                              "zh-CN"
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <Button
                              variant="ghost"
                              size="icon-sm"
                              aria-label={`删除 ${user.name}`}
                              title="删除用户及对话"
                              disabled={busy || user.user_id === me.user_id}
                              onClick={() => void remove(user)}
                            >
                              <Trash2 className="size-4 text-destructive" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex items-center justify-end gap-3 border-t p-3 text-xs text-muted-foreground">
                  <span>
                    {count === 0 ? 0 : offset + 1}–
                    {Math.min(offset + users.length, count)} / {count}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={busy || offset === 0}
                    onClick={() => void load(Math.max(0, offset - 50))}
                  >
                    上一页
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={busy || offset + users.length >= count}
                    onClick={() => void load(offset + 50)}
                  >
                    下一页
                  </Button>
                </div>
              </div>
            </>
          )
        )}
      </div>
    </main>
  )
}
