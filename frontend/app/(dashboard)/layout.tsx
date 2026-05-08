import { redirect } from 'next/navigation'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { LogoutButton } from '@/components/dashboard/LogoutButton'
import { NotificationBadge } from '@/components/dashboard/NotificationBadge'
import { serverFetch } from '@/lib/api'
import type { Me, Farm, PaginatedResponse } from '@/types/api'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [me, farmsData, unreadData] = await Promise.all([
    serverFetch<Me>('/auth/me/'),
    serverFetch<PaginatedResponse<Farm>>('/farms/'),
    serverFetch<{ unread_count: number }>('/notifications/unread-count/'),
  ])

  if (!me) redirect('/login')

  const farms = farmsData?.results ?? []
  const unreadCount = unreadData?.unread_count ?? 0
  const displayName = me.first_name ? `${me.first_name} ${me.last_name}`.trim() : me.username

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar farms={farms} />

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
          <div />
          <div className="flex items-center gap-3">
            <NotificationBadge initialCount={unreadCount} />
            <span className="text-sm text-slate-600">
              <strong>{displayName}</strong>
            </span>
            <LogoutButton />
          </div>
        </header>

        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
