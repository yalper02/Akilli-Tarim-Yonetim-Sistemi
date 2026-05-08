'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { clientFetch } from '@/lib/client-api'
import type { Command, PaginatedResponse } from '@/types/api'

interface Props {
  farmId: string
}

const ACTION_LABELS: Record<string, string> = {
  open_valve: 'Vana Aç',
  close_valve: 'Vana Kapat',
  dispense_fertilizer: 'Gübre Ver',
}

const STATUS_CONFIG: Record<
  Command['status'],
  { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
> = {
  pending: { label: 'Bekliyor', variant: 'secondary' },
  sent: { label: 'Gönderildi', variant: 'secondary' },
  received: { label: 'Alındı', variant: 'outline' },
  executed: { label: 'Uygulandı', variant: 'default' },
  failed: { label: 'Başarısız', variant: 'destructive' },
}

export function RecentCommandsWidget({ farmId }: Props) {
  const { data, isPending, isError } = useQuery({
    queryKey: ['commands', farmId],
    queryFn: () =>
      clientFetch<PaginatedResponse<Command>>(`/farms/${farmId}/commands/?page_size=5`),
    refetchInterval: 30_000,
  })

  const commands = data?.results ?? []

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Son Komutlar</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="animate-pulse space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex justify-between">
                <div className="h-4 w-28 rounded bg-slate-100" />
                <div className="h-4 w-16 rounded bg-slate-100" />
              </div>
            ))}
          </div>
        )}

        {isError && <p className="text-sm text-slate-400">Komutlar yüklenemedi.</p>}

        {!isPending && !isError && commands.length === 0 && (
          <p className="text-sm text-slate-400">Henüz komut gönderilmedi.</p>
        )}

        {commands.length > 0 && (
          <ul className="space-y-2">
            {commands.map((cmd) => {
              const cfg = STATUS_CONFIG[cmd.status] ?? {
                label: cmd.status,
                variant: 'secondary' as const,
              }
              return (
                <li key={cmd.id} className="flex items-center justify-between text-sm">
                  <span className="text-slate-700">
                    {ACTION_LABELS[cmd.action_type] ?? cmd.action_type}
                    <span className="ml-1 text-xs text-slate-400">
                      ({cmd.triggered_by === 'rule' ? 'otomatik' : 'manuel'})
                    </span>
                  </span>
                  <Badge variant={cfg.variant} className="text-xs">
                    {cfg.label}
                  </Badge>
                </li>
              )
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
