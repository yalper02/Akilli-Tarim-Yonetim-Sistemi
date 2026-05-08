'use client'

import { useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import type { SensorReading, Command, Notification } from '@/types/api'

/** Django ASGI sunucusunun WebSocket adresi — üretimde env var ile ezilir. */
const WS_BASE =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_BACKEND_WS_URL) ||
  'ws://localhost:8000'

type WsMessage =
  | { type: 'sensor_reading'; data: SensorReading }
  | { type: 'command_status'; data: Command }
  | { type: 'notification'; data: Notification }

/**
 * Çiftliğe ait canlı veri kanalını açar ve gelen mesajları TanStack Query
 * cache'ine yazar. Bağlantı kesilirse 3 saniye sonra otomatik yeniden bağlanır.
 */
export function useFarmLiveData(farmId: string): void {
  const queryClient = useQueryClient()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    let destroyed = false

    async function connect() {
      if (destroyed) return

      // HttpOnly cookie erişim tokenını Next.js route handler üzerinden al
      let token: string
      try {
        const res = await fetch('/api/auth/token')
        if (!res.ok) return
        const json = (await res.json()) as { access_token: string }
        token = json.access_token
      } catch {
        return
      }

      if (destroyed) return

      const ws = new WebSocket(`${WS_BASE}/ws/farms/${farmId}/live/?token=${token}`)
      wsRef.current = ws

      ws.onmessage = (event: MessageEvent<string>) => {
        let msg: WsMessage
        try {
          msg = JSON.parse(event.data) as WsMessage
        } catch {
          return
        }

        if (msg.type === 'sensor_reading') {
          // Güncel ölçüm satırını güncelle; yoksa ekle
          queryClient.setQueryData<SensorReading[]>(['sensor-data', 'latest', farmId], (old) => {
            if (!old) return [msg.data]
            const idx = old.findIndex(
              (r) => r.device === msg.data.device && r.capability_type === msg.data.capability_type,
            )
            if (idx === -1) return [...old, msg.data]
            const next = [...old]
            next[idx] = msg.data
            return next
          })
        } else if (msg.type === 'command_status') {
          // Komut geçmişi listesini yenile
          void queryClient.invalidateQueries({ queryKey: ['commands', farmId] })
        } else if (msg.type === 'notification') {
          // Bildirim listesi ve okunmamış sayacını yenile
          void queryClient.invalidateQueries({ queryKey: ['notifications'] })
        }
      }

      ws.onclose = () => {
        if (!destroyed) {
          reconnectRef.current = setTimeout(() => void connect(), 3_000)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    void connect()

    return () => {
      destroyed = true
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
      wsRef.current?.close()
      wsRef.current = null
    }
  }, [farmId, queryClient])
}
