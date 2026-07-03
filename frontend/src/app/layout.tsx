import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'VideoBrain - 短视频智能知识库',
  description: '通过短视频平台链接，一键识别视频内容并概括优化成知识库。支持抖音、B站、YouTube、快手、微信视频号等7+平台。',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        {/* 防止主题和字体大小闪烁的脚本 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  // 初始化主题
                  var theme = localStorage.getItem('videobrain-theme');
                  if (theme) {
                    document.documentElement.setAttribute('data-theme', theme);
                  } else {
                    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
                  }

                  // 初始化字体大小
                  var fontSize = localStorage.getItem('videobrain-font-size');
                  if (fontSize) {
                    document.documentElement.setAttribute('data-font-size', fontSize);
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body>
        <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
          {children}
        </main>
      </body>
    </html>
  )
}
