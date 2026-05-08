'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { clientFetch } from '@/lib/client-api'

interface WeatherData {
  temperature_2m: number
  precipitation_probability: number
  wind_speed_10m: number
  fetched_at: string
}

interface Props {
  farmId: string
}

export function WeatherWidget({ farmId }: Props) {
  const { data, isPending } = useQuery({
    queryKey: ['weather', farmId],
    queryFn: () => clientFetch<WeatherData>(`/farms/${farmId}/weather/`),
    retry: false,
  })

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Hava Durumu</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="animate-pulse space-y-2">
            <div className="h-8 w-24 rounded bg-slate-100" />
            <div className="h-4 w-32 rounded bg-slate-100" />
          </div>
        )}

        {!isPending && !data && (
          <div className="text-sm text-slate-400">
            <p>Hava durumu verisi mevcut değil.</p>
            <p className="mt-1 text-xs">
              Çiftliğe koordinat eklendikten sonra otomatik güncellenir.
            </p>
          </div>
        )}

        {data && (
          <div className="space-y-3">
            <div className="flex items-end gap-1">
              <span className="text-3xl font-bold text-slate-800">
                {data.temperature_2m.toFixed(1)}
              </span>
              <span className="mb-1 text-slate-500">°C</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="rounded bg-slate-50 p-2">
                <p className="text-xs text-slate-400">Yağış İhtimali</p>
                <p className="font-medium text-slate-700">%{data.precipitation_probability}</p>
              </div>
              <div className="rounded bg-slate-50 p-2">
                <p className="text-xs text-slate-400">Rüzgar</p>
                <p className="font-medium text-slate-700">{data.wind_speed_10m} km/s</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
