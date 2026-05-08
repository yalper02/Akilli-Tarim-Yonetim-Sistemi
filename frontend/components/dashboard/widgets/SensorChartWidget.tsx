'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { clientFetch } from '@/lib/client-api'
import type { TimeseriesPoint } from '@/types/api'

interface Props {
  farmId: string
}

const CAPABILITIES = [
  { value: 'soil_moisture', label: 'Toprak Nemi', unit: '%' },
  { value: 'temperature', label: 'Sıcaklık', unit: '°C' },
  { value: 'humidity', label: 'Hava Nemi', unit: '%' },
  { value: 'ph_level', label: 'pH', unit: '' },
  { value: 'nitrogen_level', label: 'Azot (N)', unit: 'ppm' },
  { value: 'phosphorus_level', label: 'Fosfor (P)', unit: 'ppm' },
  { value: 'potassium_level', label: 'Potasyum (K)', unit: 'ppm' },
] as const

const DATE_RANGES = [
  { label: '24 Saat', hours: 24, aggregation: 'hour' },
  { label: '7 Gün', hours: 24 * 7, aggregation: 'hour' },
  { label: '30 Gün', hours: 24 * 30, aggregation: 'day' },
] as const

function formatBucket(bucket: string, hours: number): string {
  const date = new Date(bucket)
  if (hours <= 24) {
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short' })
}

interface ChartPoint {
  time: string
  ortalama: number
  min: number
  maks: number
}

export function SensorChartWidget({ farmId }: Props) {
  const [capability, setCapability] = useState<string>('soil_moisture')
  const [rangeIndex, setRangeIndex] = useState(0)

  const range = DATE_RANGES[rangeIndex]
  const capMeta = CAPABILITIES.find((c) => c.value === capability) ?? CAPABILITIES[0]

  const now = new Date()
  const start = new Date(now.getTime() - range.hours * 3600 * 1000).toISOString()
  const end = now.toISOString()

  const { data, isPending, isError } = useQuery<TimeseriesPoint[]>({
    queryKey: ['sensor-data', 'timeseries', farmId, capability, rangeIndex],
    queryFn: () =>
      clientFetch<TimeseriesPoint[]>(
        `/sensor-data/timeseries/?farm_id=${farmId}&capability=${capability}&start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&aggregation=${range.aggregation}`,
      ),
    staleTime: 60_000,
  })

  const chartData: ChartPoint[] =
    data?.map((point) => ({
      time: formatBucket(point.bucket, range.hours),
      ortalama: +point.avg_value.toFixed(2),
      min: +point.min_value.toFixed(2),
      maks: +point.max_value.toFixed(2),
    })) ?? []

  const unitSuffix = capMeta.unit ? ` ${capMeta.unit}` : ''

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle className="text-base">Sensör Grafiği</CardTitle>
          <div className="flex flex-wrap items-center gap-2">
            {/* Ölçüm tipi seçici */}
            <select
              value={capability}
              onChange={(e) => setCapability(e.target.value)}
              className="rounded-md border border-slate-200 bg-white px-2 py-1 text-sm text-slate-700 focus:ring-2 focus:ring-green-500 focus:outline-none"
            >
              {CAPABILITIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>

            {/* Tarih aralığı butonları */}
            <div className="flex overflow-hidden rounded-md border border-slate-200 bg-white">
              {DATE_RANGES.map((r, i) => (
                <button
                  key={r.label}
                  onClick={() => setRangeIndex(i)}
                  className={`px-3 py-1 text-sm transition-colors ${
                    i === rangeIndex
                      ? 'bg-green-600 text-white'
                      : 'text-slate-600 hover:bg-slate-50'
                  } ${i > 0 ? 'border-l border-slate-200' : ''}`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {isPending && (
          <div className="flex h-52 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-500 border-t-transparent" />
          </div>
        )}

        {isError && (
          <div className="flex h-52 items-center justify-center">
            <p className="text-sm text-slate-400">Grafik verileri yüklenemedi.</p>
          </div>
        )}

        {!isPending && !isError && chartData.length === 0 && (
          <div className="flex h-52 items-center justify-center">
            <p className="text-sm text-slate-400">Bu dönem için sensör verisi yok.</p>
          </div>
        )}

        {!isPending && !isError && chartData.length > 0 && (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={false}
                unit={unitSuffix}
                width={60}
              />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 8,
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 2px 8px rgba(0,0,0,.06)',
                }}
                formatter={(value) =>
                  value != null ? [`${value}${unitSuffix}`, undefined] : ['-', undefined]
                }
              />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
              <Line
                type="monotone"
                dataKey="ortalama"
                name="Ortalama"
                stroke="#16a34a"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="min"
                name="Min"
                stroke="#94a3b8"
                strokeWidth={1}
                strokeDasharray="4 4"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="maks"
                name="Maks"
                stroke="#64748b"
                strokeWidth={1}
                strokeDasharray="4 4"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
