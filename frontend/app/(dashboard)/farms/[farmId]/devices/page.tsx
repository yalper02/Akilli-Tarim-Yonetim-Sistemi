'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { clientFetch } from '@/lib/client-api'
import type { Device, PaginatedResponse } from '@/types/api'

const TYPE_LABELS: Record<string, string> = {
  sensor: 'Sensör',
  actuator: 'Aktüatör',
  combined: 'Karma',
}

const CAPABILITY_LABELS: Record<string, string> = {
  soil_moisture: 'Toprak Nemi',
  temperature: 'Sıcaklık',
  humidity: 'Hava Nemi',
  ph_level: 'pH',
  nitrogen_level: 'Azot',
  phosphorus_level: 'Fosfor',
  potassium_level: 'Potasyum',
  valve_control: 'Vana',
  fertilizer_dispenser: 'Gübre',
}

function formatRelative(dateStr: string | null): string {
  if (!dateStr) return 'Hiç görülmedi'
  const diff = Date.now() - new Date(dateStr).getTime()
  const min = Math.floor(diff / 60_000)
  if (min < 1) return 'Az önce'
  if (min < 60) return `${min} dk önce`
  const h = Math.floor(min / 60)
  if (h < 24) return `${h} sa önce`
  return `${Math.floor(h / 24)} gün önce`
}

// ---------- Create Modal ----------

interface CreateModalProps {
  farmId: string
  onClose: () => void
}

function CreateDeviceModal({ farmId, onClose }: CreateModalProps) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    name: '',
    device_uid: '',
    device_type: 'sensor' as Device['device_type'],
    location_description: '',
  })
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: (body: typeof form) =>
      clientFetch<Device>(`/farms/${farmId}/devices/`, {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['devices', farmId] })
      onClose()
    },
    onError: () => setError('Cihaz oluşturulamadı. Bilgileri kontrol edin.'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold text-slate-800">Yeni Cihaz Ekle</h2>

        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Cihaz Adı</label>
            <Input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="Sensör A-01"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Cihaz UID</label>
            <Input
              value={form.device_uid}
              onChange={(e) => setForm((f) => ({ ...f, device_uid: e.target.value }))}
              placeholder="device-sensor-001"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Tür</label>
            <select
              value={form.device_type}
              onChange={(e) =>
                setForm((f) => ({ ...f, device_type: e.target.value as Device['device_type'] }))
              }
              className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
            >
              <option value="sensor">Sensör</option>
              <option value="actuator">Aktüatör</option>
              <option value="combined">Karma</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Konum (isteğe bağlı)
            </label>
            <Input
              value={form.location_description}
              onChange={(e) => setForm((f) => ({ ...f, location_description: e.target.value }))}
              placeholder="Kuzey tarla, sıra 3"
            />
          </div>
        </div>

        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={mutation.isPending}>
            İptal
          </Button>
          <Button
            onClick={() => mutation.mutate(form)}
            disabled={mutation.isPending || !form.name || !form.device_uid}
            className="bg-green-600 hover:bg-green-700"
          >
            {mutation.isPending ? 'Kaydediliyor…' : 'Kaydet'}
          </Button>
        </div>
      </div>
    </div>
  )
}

// ---------- Delete Modal ----------

interface DeleteModalProps {
  device: Device
  farmId: string
  onClose: () => void
}

function DeleteDeviceModal({ device, farmId, onClose }: DeleteModalProps) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => clientFetch<void>(`/devices/${device.id}/`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['devices', farmId] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-2 text-lg font-semibold text-slate-800">Cihazı Sil</h2>
        <p className="mb-5 text-sm text-slate-500">
          <strong>{device.name}</strong> cihazını silmek istediğinize emin misiniz? Bu işlem geri
          alınamaz.
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={mutation.isPending}>
            İptal
          </Button>
          <Button
            variant="destructive"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Siliniyor…' : 'Sil'}
          </Button>
        </div>
      </div>
    </div>
  )
}

// ---------- Main Page ----------

export default function DevicesPage() {
  const params = useParams()
  const farmId = params.farmId as string

  const [showCreate, setShowCreate] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Device | null>(null)

  const { data, isPending, isError } = useQuery({
    queryKey: ['devices', farmId],
    queryFn: () =>
      clientFetch<PaginatedResponse<Device>>(`/farms/${farmId}/devices/?page_size=100`),
  })

  const devices = data?.results ?? []

  return (
    <>
      {showCreate && <CreateDeviceModal farmId={farmId} onClose={() => setShowCreate(false)} />}
      {deleteTarget && (
        <DeleteDeviceModal
          device={deleteTarget}
          farmId={farmId}
          onClose={() => setDeleteTarget(null)}
        />
      )}

      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-slate-800">Cihazlar</h1>
          <Button onClick={() => setShowCreate(true)} className="bg-green-600 hover:bg-green-700">
            + Cihaz Ekle
          </Button>
        </div>

        {isPending && (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100" />
            ))}
          </div>
        )}

        {isError && <p className="text-sm text-slate-400">Cihazlar yüklenemedi.</p>}

        {!isPending && !isError && devices.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-slate-400">Bu çiftlikte henüz cihaz yok.</p>
              <Button
                className="mt-4 bg-green-600 hover:bg-green-700"
                onClick={() => setShowCreate(true)}
              >
                İlk Cihazı Ekle
              </Button>
            </CardContent>
          </Card>
        )}

        {devices.length > 0 && (
          <div className="space-y-3">
            {devices.map((device) => (
              <Card key={device.id} className="transition-shadow hover:shadow-md">
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-center gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/farms/${farmId}/devices/${device.id}`}
                          className="font-medium text-slate-800 hover:text-green-700"
                        >
                          {device.name}
                        </Link>
                        <Badge
                          variant={device.status === 'online' ? 'default' : 'secondary'}
                          className={
                            device.status === 'online'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-slate-100 text-slate-500'
                          }
                        >
                          {device.status === 'online' ? 'Çevrimiçi' : 'Çevrimdışı'}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {TYPE_LABELS[device.device_type] ?? device.device_type}
                        </Badge>
                      </div>
                      <p className="mt-0.5 text-xs text-slate-400">
                        {device.device_uid}
                        {device.location_description && ` · ${device.location_description}`}
                      </p>
                      {device.capabilities.length > 0 && (
                        <p className="mt-1 text-xs text-slate-400">
                          {device.capabilities
                            .map((c) => CAPABILITY_LABELS[c.capability_type] ?? c.capability_type)
                            .join(', ')}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400">
                      {formatRelative(device.last_seen_at)}
                    </span>
                    <Link href={`/farms/${farmId}/devices/${device.id}`}>
                      <Button variant="outline" size="sm">
                        Detay
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-red-500 hover:border-red-300 hover:text-red-600"
                      onClick={() => setDeleteTarget(device)}
                    >
                      Sil
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </>
  )
}
