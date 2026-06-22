// src/app/layout.tsx

import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "My AI App",
  description: "Next.js + FastAPI + DeepSeek Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        {/*
          整个页面的最外层容器。
          min-h-screen 表示最小高度是整个屏幕高度。
        */}
        <div className="min-h-screen bg-background text-foreground">
          {/*
            顶部导航栏。
            这里会出现在所有页面中。
          */}
          <header className="border-b">
            <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
              {/*
                左侧网站名称。
                Link 是 Next.js 提供的页面跳转组件。
                href="/" 表示点击后回到首页。
              */}
              <Link href="/" className="text-lg font-bold">
                My AI App
              </Link>

              {/*
                右侧导航链接。
                点击后会进入对应的前端页面。
              */}
              <nav className="flex items-center gap-4 text-sm">
                <Link href="/" className="hover:underline">
                  首页
                </Link>

                <Link href="/chat" className="hover:underline">
                  聊天
                </Link>
              </nav>
            </div>
          </header>

          {/*
            main 是页面主体区域。
            每个 page.tsx 的内容都会显示在这里。
          */}
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
