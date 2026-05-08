'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { clientFetch } from '@/lib/client-api'
import type { Notification, PaginatedResponse } from '@/types/api'

interface Props {
  farmId: string
}

const SEVERITY_CONFIG: Record<
  Notification['severity'],
  { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
> = {
  info: { label: 'Bilgi', variant: 'secondary' },
  warning: { label: 'Uyarı', variant: 'outline' },
  critical: { label: 'Kritik', variant: 'destructive' },
}

export function ActiveNotificationsWidget({ farmId: _farmId }: Props) {
  const { data, isPending, isError } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () =>
      clientFetch<PaginatedResponse<Notification>>(`/notifications/?is_read=false&page_size=5`),
    refetchInterval: 60_000,
  })

  const notifications = data?.results ?? []

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Aktif Bildirimler</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="animate-pulse space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-4 w-full rounded bg-slate-100" />
            ))}
          </div>
        )}

        {isError && <p className="text-sm text-slate-400">Bildirimler yüklenemedi.</p>}

        {!isPending && !isError && notifications.length === 0 && (
          <p className="text-sm text-slate-400">Okunmamış bildirim yok. ✓</p>
        )}

        {notifications.length > 0 && (
          <ul className="space-y-2">
            {notifications.map((n) => {
              const cfg = SEVERITY_CONFIG[n.severity] ?? {
                label: n.severity,
                variant: 'secondary' as const,
              }
              return (
                <li key={n.id} className="flex items-start gap-2 text-sm">
                  <Badge variant={cfg.variant} className="mt-0.5 shrink-0 text-xs">
                    {cfg.label}
                  </Badge>
                  <span className="text-slate-700">{n.message}</span>
                </li>
              )
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
