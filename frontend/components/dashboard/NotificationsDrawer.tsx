'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { clientFetch } from '@/lib/client-api'
import type { Notification, PaginatedResponse } from '@/types/api'

const SEVERITY_CONFIG: Record<Notification['severity'], { label: string; className: string }> = {
  info: { label: 'Bilgi', className: 'bg-blue-50 text-blue-700' },
  warning: { label: 'Uyarı', className: 'bg-amber-50 text-amber-700' },
  critical: { label: 'Kritik', className: 'bg-red-50 text-red-700' },
}

function formatTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const min = Math.floor(diff / 60_000)
  if (min < 1) return 'Az önce'
  if (min < 60) return `${min} dk önce`
  const h = Math.floor(min / 60)
  if (h < 24) return `${h} sa önce`
  return `${Math.floor(h / 24)} gün önce`
}

interface Props {
  onClose: () => void
}

export function NotificationsDrawer({ onClose }: Props) {
  const queryClient = useQueryClient()
  const [severityFilter, setSeverityFilter] = useState<string>('all')

  const { data, isPending } = useQuery({
    queryKey: ['notifications', 'list'],
    queryFn: () => clientFetch<PaginatedResponse<Notification>>('/notifications/?page_size=50'),
    refetchInterval: 30_000,
  })

  const markReadMutation = useMutation({
    mutationFn: (id: number) => clientFetch(`/notifications/${id}/mark-read/`, { method: 'POST' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const markAllMutation = useMutation({
    mutationFn: () => clientFetch('/notifications/mark-all-read/', { method: 'POST' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const notifications = data?.results ?? []
  const filtered =
    severityFilter === 'all'
      ? notifications
      : notifications.filter((n) => n.severity === severityFilter)

  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <>
      {/* Arka plan kapanma alanı */}
      <div className="fixed inset-0 z-40 bg-black/20" onClick={onClose} />

      {/* Drawer */}
      <div className="fixed top-0 right-0 z-50 flex h-full w-full max-w-sm flex-col bg-white shadow-2xl">
        {/* Başlık */}
        <div className="flex items-center justify-between border-b border-slate-200 p-4">
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-slate-800">Bildirimler</h2>
            {unreadCount > 0 && (
              <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs font-bold text-white">
                {unreadCount}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            ✕
          </button>
        </div>

        {/* Filtre + Tümünü okundu işaretle */}
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-2">
          <div className="flex gap-1">
            {(['all', 'info', 'warning', 'critical'] as const).map((s) => (
              <button
                key={s}
                onClick={() => setSeverityFilter(s)}
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
                  severityFilter === s
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                {s === 'all'
                  ? 'Tümü'
                  : s === 'info'
                    ? 'Bilgi'
                    : s === 'warning'
                      ? 'Uyarı'
                      : 'Kritik'}
              </button>
            ))}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={() => markAllMutation.mutate()}
              disabled={markAllMutation.isPending}
              className="text-xs text-slate-400 hover:text-green-600"
            >
              Tümünü okundu işaretle
            </button>
          )}
        </div>

        {/* Liste */}
        <div className="flex-1 overflow-y-auto">
          {isPending && (
            <div className="space-y-2 p-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-16 animate-pulse rounded-lg bg-slate-100" />
              ))}
            </div>
          )}

          {!isPending && filtered.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <p className="text-sm text-slate-400">Bildirim bulunamadı.</p>
            </div>
          )}

          {filtered.map((n) => {
            const sev = SEVERITY_CONFIG[n.severity]
            return (
              <div
                key={n.id}
                className={`border-b border-slate-50 p-4 transition-colors ${
                  n.is_read ? 'bg-white' : 'bg-slate-50'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-1.5">
                      {!n.is_read && <span className="h-2 w-2 shrink-0 rounded-full bg-blue-500" />}
                      <Badge className={`text-xs ${sev.className}`}>{sev.label}</Badge>
                      <span className="text-xs text-slate-400">{formatTime(n.created_at)}</span>
                    </div>
                    {n.title && (
                      <p className="mt-1 text-sm font-medium text-slate-800">{n.title}</p>
                    )}
                    <p className="mt-0.5 text-sm text-slate-600">{n.message}</p>
                  </div>
                  {!n.is_read && (
                    <button
                      onClick={() => markReadMutation.mutate(n.id)}
                      className="shrink-0 text-xs text-slate-400 hover:text-green-600"
                    >
                      ✓
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </>
  )
}
