'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { clientFetch } from '@/lib/client-api'
import type { Rule, PaginatedResponse, Device, RuleCondition, RuleAction } from '@/types/api'

const CAPABILITY_LABELS: Record<string, string> = {
  soil_moisture: 'Toprak Nemi',
  temperature: 'Sıcaklık',
  humidity: 'Hava Nemi',
  ph_level: 'pH',
  nitrogen_level: 'Azot',
  phosphorus_level: 'Fosfor',
  potassium_level: 'Potasyum',
}

const OPERATOR_LABELS: Record<string, string> = {
  lt: '<',
  lte: '≤',
  gt: '>',
  gte: '≥',
  eq: '=',
}

const ACTION_LABELS: Record<string, string> = {
  open_valve: 'Vana Aç',
  close_valve: 'Vana Kapat',
  dispense_fertilizer: 'Gübre Ver',
}

// ---------- Create Modal ----------

interface CreateRuleModalProps {
  farmId: string
  onClose: () => void
}

function emptyCondition(): Omit<RuleCondition, 'id'> {
  return { capability_type: 'soil_moisture', operator: 'lt', threshold_value: 30 }
}

function emptyAction(deviceId: number): Omit<RuleAction, 'id'> {
  return { action_type: 'open_valve', device: deviceId, parameters: {}, priority: 1 }
}

function CreateRuleModal({ farmId, onClose }: CreateRuleModalProps) {
  const queryClient = useQueryClient()

  const { data: devicesData } = useQuery({
    queryKey: ['devices', farmId],
    queryFn: () =>
      clientFetch<PaginatedResponse<Device>>(`/farms/${farmId}/devices/?page_size=100`),
  })
  const devices = devicesData?.results ?? []
  const firstDeviceId = devices[0]?.id ?? 0

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [conditions, setConditions] = useState<Omit<RuleCondition, 'id'>[]>([emptyCondition()])
  const [actions, setActions] = useState<Omit<RuleAction, 'id'>[]>([emptyAction(firstDeviceId)])
  const [rainPct, setRainPct] = useState<number | null>(null)
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () =>
      clientFetch<Rule>(`/farms/${farmId}/rules/`, {
        method: 'POST',
        body: JSON.stringify({
          name,
          description,
          is_active: true,
          conditions,
          actions,
          weather_constraint:
            rainPct !== null ? { max_rain_probability_pct: rainPct, check_hours_ahead: 24 } : null,
        }),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['rules', farmId] })
      onClose()
    },
    onError: () => setError('Kural oluşturulamadı. Bilgileri kontrol edin.'),
  })

  function updateCondition<K extends keyof Omit<RuleCondition, 'id'>>(
    i: number,
    key: K,
    value: Omit<RuleCondition, 'id'>[K],
  ) {
    setConditions((prev) => prev.map((c, idx) => (idx === i ? { ...c, [key]: value } : c)))
  }

  function updateAction<K extends keyof Omit<RuleAction, 'id'>>(
    i: number,
    key: K,
    value: Omit<RuleAction, 'id'>[K],
  ) {
    setActions((prev) => prev.map((a, idx) => (idx === i ? { ...a, [key]: value } : a)))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 pt-10">
      <div className="w-full max-w-xl rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-5 text-lg font-semibold text-slate-800">Yeni Kural Oluştur</h2>

        <div className="mb-4 space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Kural Adı</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Düşük nem sulama"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Açıklama (isteğe bağlı)
            </label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Toprak nemi %30 altına düşünce..."
            />
          </div>
        </div>

        {/* Koşullar */}
        <div className="mb-4">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-medium text-slate-700">Koşullar (VE)</p>
            <button
              onClick={() => setConditions((c) => [...c, emptyCondition()])}
              className="text-xs text-green-600 hover:underline"
            >
              + Koşul Ekle
            </button>
          </div>
          <div className="space-y-2">
            {conditions.map((cond, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-slate-50 p-2">
                <select
                  value={cond.capability_type}
                  onChange={(e) => updateCondition(i, 'capability_type', e.target.value)}
                  className="flex-1 rounded border border-slate-200 bg-white px-2 py-1 text-sm"
                >
                  {Object.entries(CAPABILITY_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>
                      {l}
                    </option>
                  ))}
                </select>
                <select
                  value={cond.operator}
                  onChange={(e) => updateCondition(i, 'operator', e.target.value)}
                  className="w-16 rounded border border-slate-200 bg-white px-2 py-1 text-sm"
                >
                  {Object.entries(OPERATOR_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>
                      {l}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  value={cond.threshold_value}
                  onChange={(e) => updateCondition(i, 'threshold_value', Number(e.target.value))}
                  className="w-20 rounded border border-slate-200 px-2 py-1 text-sm"
                />
                {conditions.length > 1 && (
                  <button
                    onClick={() => setConditions((c) => c.filter((_, idx) => idx !== i))}
                    className="text-slate-400 hover:text-red-500"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Eylemler */}
        <div className="mb-4">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-medium text-slate-700">Eylemler</p>
            <button
              onClick={() => setActions((a) => [...a, emptyAction(devices[0]?.id ?? 0)])}
              className="text-xs text-green-600 hover:underline"
            >
              + Eylem Ekle
            </button>
          </div>
          <div className="space-y-2">
            {actions.map((act, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-slate-50 p-2">
                <select
                  value={act.action_type}
                  onChange={(e) => updateAction(i, 'action_type', e.target.value)}
                  className="flex-1 rounded border border-slate-200 bg-white px-2 py-1 text-sm"
                >
                  {Object.entries(ACTION_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>
                      {l}
                    </option>
                  ))}
                </select>
                <select
                  value={act.device}
                  onChange={(e) => updateAction(i, 'device', Number(e.target.value))}
                  className="flex-1 rounded border border-slate-200 bg-white px-2 py-1 text-sm"
                >
                  {devices.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                  {devices.length === 0 && (
                    <option value={0} disabled>
                      Cihaz bulunamadı
                    </option>
                  )}
                </select>
                {actions.length > 1 && (
                  <button
                    onClick={() => setActions((a) => a.filter((_, idx) => idx !== i))}
                    className="text-slate-400 hover:text-red-500"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Hava durumu kısıtı */}
        <div className="mb-5 rounded-lg bg-blue-50 p-3">
          <div className="mb-2 flex items-center gap-2">
            <input
              type="checkbox"
              id="weather-check"
              checked={rainPct !== null}
              onChange={(e) => setRainPct(e.target.checked ? 40 : null)}
              className="rounded"
            />
            <label htmlFor="weather-check" className="text-sm font-medium text-slate-700">
              Yağmur tahmini yüksekse iptal et (FR-03)
            </label>
          </div>
          {rainPct !== null && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-600">Yağmur olasılığı</span>
              <input
                type="number"
                min={10}
                max={100}
                value={rainPct}
                onChange={(e) => setRainPct(Number(e.target.value))}
                className="w-20 rounded border border-slate-200 px-2 py-1 text-sm"
              />
              <span className="text-sm text-slate-600">% üzerindeyse tetikleme</span>
            </div>
          )}
        </div>

        {error && <p className="mb-3 text-sm text-red-500">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={mutation.isPending}>
            İptal
          </Button>
          <Button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !name || devices.length === 0}
            className="bg-green-600 hover:bg-green-700"
          >
            {mutation.isPending ? 'Kaydediliyor…' : 'Kaydet'}
          </Button>
        </div>
      </div>
    </div>
  )
}

// ---------- Main Page ----------

export default function RulesPage() {
  const params = useParams()
  const farmId = params.farmId as string
  const queryClient = useQueryClient()

  const [showCreate, setShowCreate] = useState(false)

  const { data, isPending, isError } = useQuery({
    queryKey: ['rules', farmId],
    queryFn: () => clientFetch<PaginatedResponse<Rule>>(`/farms/${farmId}/rules/?page_size=100`),
  })

  const toggleMutation = useMutation({
    mutationFn: (ruleId: number) => clientFetch(`/rules/${ruleId}/toggle/`, { method: 'POST' }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['rules', farmId] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (ruleId: number) => clientFetch(`/rules/${ruleId}/`, { method: 'DELETE' }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['rules', farmId] }),
  })

  const rules = data?.results ?? []

  return (
    <>
      {showCreate && <CreateRuleModal farmId={farmId} onClose={() => setShowCreate(false)} />}

      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-slate-800">Kurallar</h1>
          <Button onClick={() => setShowCreate(true)} className="bg-green-600 hover:bg-green-700">
            + Kural Ekle
          </Button>
        </div>

        {isPending && (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100" />
            ))}
          </div>
        )}

        {isError && <p className="text-sm text-slate-400">Kurallar yüklenemedi.</p>}

        {!isPending && !isError && rules.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-slate-400">Bu çiftlikte henüz kural yok.</p>
              <Button
                className="mt-4 bg-green-600 hover:bg-green-700"
                onClick={() => setShowCreate(true)}
              >
                İlk Kuralı Oluştur
              </Button>
            </CardContent>
          </Card>
        )}

        {rules.length > 0 && (
          <div className="space-y-3">
            {rules.map((rule) => (
              <Card key={rule.id} className={rule.is_active ? '' : 'opacity-60'}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-slate-800">{rule.name}</span>
                        <Badge
                          className={
                            rule.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-slate-100 text-slate-500'
                          }
                        >
                          {rule.is_active ? 'Aktif' : 'Pasif'}
                        </Badge>
                      </div>
                      {rule.description && (
                        <p className="mt-0.5 text-xs text-slate-400">{rule.description}</p>
                      )}
                      <div className="mt-2 flex flex-wrap gap-1">
                        {rule.conditions.map((c) => (
                          <span
                            key={c.id}
                            className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
                          >
                            {CAPABILITY_LABELS[c.capability_type] ?? c.capability_type}{' '}
                            {OPERATOR_LABELS[c.operator] ?? c.operator} {c.threshold_value}
                          </span>
                        ))}
                        {rule.conditions.length > 0 && rule.actions.length > 0 && (
                          <span className="px-1 text-xs text-slate-400">→</span>
                        )}
                        {rule.actions.map((a) => (
                          <span
                            key={a.id}
                            className="rounded bg-green-50 px-2 py-0.5 text-xs text-green-700"
                          >
                            {ACTION_LABELS[a.action_type] ?? a.action_type}
                          </span>
                        ))}
                        {rule.weather_constraint && (
                          <span className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600">
                            🌧 {'>'} %{rule.weather_constraint.max_rain_probability_pct} iptal
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex shrink-0 items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleMutation.mutate(rule.id)}
                        disabled={toggleMutation.isPending}
                      >
                        {rule.is_active ? 'Duraklat' : 'Etkinleştir'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-500 hover:border-red-300 hover:text-red-600"
                        onClick={() => {
                          if (window.confirm(`"${rule.name}" kuralı silinsin mi?`)) {
                            deleteMutation.mutate(rule.id)
                          }
                        }}
                        disabled={deleteMutation.isPending}
                      >
                        Sil
                      </Button>
                    </div>
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
