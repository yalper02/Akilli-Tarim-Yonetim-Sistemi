'use client'

import { useFarmLiveData } from '@/hooks/useFarmLiveData'

interface Props {
  farmId: string
}

/**
 * WebSocket bağlantısını yöneten görünmez Client bileşeni.
 * Server Component olan dashboard sayfasından çağrılır.
 */
export function FarmLiveDataSync({ farmId }: Props) {
  useFarmLiveData(farmId)
  return null
}
