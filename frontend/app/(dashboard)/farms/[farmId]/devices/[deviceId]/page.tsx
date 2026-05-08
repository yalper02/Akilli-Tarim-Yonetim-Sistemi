'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { clientFetch } from '@/lib/client-api'
import { SensorChartWidget } from '@/components/dashboard/widgets/SensorChartWidget'
import type { Device, DeviceHealth, PaginatedResponse, SensorReading } from '@/types/api'

const ACTION_OPTIONS = [
  { value: 'open_valve', label: 'Vana Aç', forType: ['actuator', 'combined'] },
  { value: 'close_valve', label: 'Vana Kapat', forType: ['actuator', 'combined'] },
  { value: 'dispense_fertilizer', label: 'Gübre Ver', forType: ['actuator', 'combined'] },
]

const CAPABILITY_LABELS: Record<string, string> = {
  soil_moisture: 'Toprak Nemi',
  temperature: 'Sıcaklık',
  humidity: 'Hava Nemi',
  ph_level: 'pH',
  nitrogen_level: 'Azot',
  phosphorus_level: 'Fosfor',
  potassium_level: 'Potasyum',
  valve_control: 'Vana Kontrolü',
  fertilizer_dispenser: 'Gübre Haznesi',
}

function batteryColor(level: number | null): string {
  if (level === null) return 'text-slate-400'
  if (level > 40) return 'text-green-600'
  if (level > 20) return 'text-amber-500'
  return 'text-red-500'
}

// ---------- Manuel Komut Paneli ----------

interface CommandPanelProps {
  deviceId: string
  deviceType: Device['device_type']
}

function ManualCommandPanel({ deviceId, deviceType }: CommandPanelProps) {
  const [action, setAction] = useState('open_valve')
  const [duration, setDuration] = useState(1800)
  const [success, setSuccess] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  const availableActions = ACTION_OPTIONS.filter((a) => a.forType.includes(deviceType))

  const mutation = useMutation({
    mutationFn: () => {
      const params: Record<string, unknown> =
        action === 'open_valve' ? { duration_seconds: duration } : {}
      return clientFetch(`/devices/${deviceId}/commands/`, {
        method: 'POST',
        body: JSON.stringify({ action_type: action, parameters: params }),
      })
    },
    onSuccess: () => {
      setSuccess(true)
      setErrorMsg('')
      setTimeout(() => setSuccess(false), 3000)
    },
    onError: () => setErrorMsg('Komut gönderilemedi.'),
  })

  if (availableActions.length === 0) return null

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Manuel Komut (US-02)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">İşlem</label>
          <select
            value={action}
            onChange={(e) => setAction(e.target.value)}
            className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
          >
            {availableActions.map((a) => (
              <option key={a.value} value={a.value}>
                {a.label}
              </option>
            ))}
          </select>
        </div>

        {action === 'open_valve' && (
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Süre (saniye)</label>
            <input
              type="number"
              min={60}
              max={7200}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
            />
            <p className="mt-1 text-xs text-slate-400">
              {Math.floor(duration / 60)} dakika{' '}
              {duration % 60 > 0 ? `${duration % 60} saniye` : ''}
            </p>
          </div>
        )}

        {errorMsg && <p className="text-sm text-red-500">{errorMsg}</p>}
        {success && (
          <p className="text-sm font-medium text-green-600">Komut başarıyla gönderildi.</p>
        )}

        <Button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="w-full bg-green-600 hover:bg-green-700"
        >
          {mutation.isPending ? 'Gönderiliyor…' : 'Komutu Gönder'}
        </Button>
      </CardContent>
    </Card>
  )
}

// ---------- Main Page ----------

export default function DeviceDetailPage() {
  const params = useParams()
  const farmId = params.farmId as string
  const deviceId = params.deviceId as string

  const { data: device, isPending: deviceLoading } = useQuery({
    queryKey: ['device', deviceId],
    queryFn: () => clientFetch<Device>(`/devices/${deviceId}/`),
  })

  const { data: health } = useQuery({
    queryKey: ['device-health', deviceId],
    queryFn: () => clientFetch<DeviceHealth>(`/devices/${deviceId}/health/`),
    refetchInterval: 30_000,
  })

  const { data: latestReadings } = useQuery({
    queryKey: ['sensor-data', 'latest', farmId, deviceId],
    queryFn: () => clientFetch<SensorReading[]>(`/sensor-data/latest/?device_id=${deviceId}`),
    refetchInterval: 60_000,
  })

  if (deviceLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-slate-100" />
        <div className="h-40 animate-pulse rounded-xl bg-slate-100" />
      </div>
    )
  }

  if (!device) {
    return <p className="text-sm text-slate-400">Cihaz bulunamadı.</p>
  }

  return (
    <div className="space-y-5">
      {/* Başlık */}
      <div className="flex items-center gap-3">
        <Link
          href={`/farms/${farmId}/devices`}
          className="text-sm text-slate-400 hover:text-slate-600"
        >
          ← Cihazlar
        </Link>
        <h1 className="text-2xl font-semibold text-slate-800">{device.name}</h1>
        <Badge
          className={
            device.status === 'online'
              ? 'bg-green-100 text-green-700'
              : 'bg-slate-100 text-slate-500'
          }
        >
          {device.status === 'online' ? 'Çevrimiçi' : 'Çevrimdışı'}
        </Badge>
      </div>

      {/* Sağlık İstatistikleri */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500">Pil</p>
            <p
              className={`mt-1 text-2xl font-semibold ${batteryColor(health?.battery_level ?? null)}`}
            >
              {health?.battery_level != null ? `${health.battery_level}%` : '—'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500">Sinyal (RSSI)</p>
            <p className="mt-1 text-2xl font-semibold text-slate-800">
              {health?.rssi != null ? `${health.rssi} dBm` : '—'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500">Cihaz UID</p>
            <p className="mt-1 font-mono text-sm text-slate-700">{device.device_uid}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500">Konum</p>
            <p className="mt-1 text-sm text-slate-700">{device.location_description || '—'}</p>
          </CardContent>
        </Card>
      </div>

      {/* Yetenekler */}
      {device.capabilities.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Yetenekler</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {device.capabilities.map((cap) => (
                <Badge key={cap.id} variant="outline">
                  {CAPABILITY_LABELS[cap.capability_type] ?? cap.capability_type}
                  {cap.unit ? ` (${cap.unit})` : ''}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Güncel Ölçümler */}
      {latestReadings && latestReadings.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Son Ölçümler</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {latestReadings.map((r) => (
                <div key={r.id} className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs text-slate-500">
                    {CAPABILITY_LABELS[r.capability_type] ?? r.capability_type}
                  </p>
                  <p className="mt-1 text-lg font-semibold text-slate-800">{r.value.toFixed(1)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Zaman serisi grafiği */}
      <SensorChartWidget farmId={farmId} />

      {/* Manuel komut paneli */}
      <ManualCommandPanel deviceId={deviceId} deviceType={device.device_type} />
    </div>
  )
}
