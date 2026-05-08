'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { clientFetch } from '@/lib/client-api'
import type { SensorReading } from '@/types/api'

interface Props {
  farmId: string
}

const CAPABILITY_META: Record<string, { label: string; unit: string; emoji: string }> = {
  soil_moisture: { label: 'Toprak Nemi', unit: '%', emoji: '💧' },
  temperature: { label: 'Sıcaklık', unit: '°C', emoji: '🌡️' },
  humidity: { label: 'Hava Nemi', unit: '%', emoji: '🌫️' },
  ph_level: { label: 'pH', unit: '', emoji: '⚗️' },
  nitrogen_level: { label: 'Azot (N)', unit: 'ppm', emoji: '🌿' },
  phosphorus_level: { label: 'Fosfor (P)', unit: 'ppm', emoji: '🔬' },
  potassium_level: { label: 'Potasyum (K)', unit: 'ppm', emoji: '⚡' },
}

function ReadingSkeleton() {
  return (
    <div className="animate-pulse rounded-lg bg-slate-100 p-4">
      <div className="mb-2 h-3 w-20 rounded bg-slate-200" />
      <div className="h-6 w-14 rounded bg-slate-200" />
    </div>
  )
}

export function CurrentReadingsWidget({ farmId }: Props) {
  const { data, isPending, isError } = useQuery({
    queryKey: ['sensor-data', 'latest', farmId],
    queryFn: () => clientFetch<SensorReading[]>(`/sensor-data/latest/?farm_id=${farmId}`),
    refetchInterval: 60_000,
  })

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Güncel Ölçümler</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <ReadingSkeleton key={i} />
            ))}
          </div>
        )}

        {isError && <p className="text-sm text-slate-400">Ölçümler yüklenemedi.</p>}

        {data && data.length === 0 && (
          <p className="text-sm text-slate-400">Henüz sensör verisi yok.</p>
        )}

        {data && data.length > 0 && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {data.map((reading) => {
              const meta = CAPABILITY_META[reading.capability_type]
              const label = meta?.label ?? reading.capability_type
              const unit = meta?.unit ?? ''
              const emoji = meta?.emoji ?? '📊'
              return (
                <div key={reading.id} className="rounded-lg bg-slate-50 p-4">
                  <p className="mb-1 text-xs text-slate-500">
                    {emoji} {label}
                  </p>
                  <p className="text-lg font-semibold text-slate-800">
                    {reading.value.toFixed(1)}
                    {unit && (
                      <span className="ml-0.5 text-sm font-normal text-slate-500">{unit}</span>
                    )}
                  </p>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
