import { serverFetch } from '@/lib/api'
import { FarmLiveDataSync } from '@/components/dashboard/FarmLiveDataSync'
import { CurrentReadingsWidget } from '@/components/dashboard/widgets/CurrentReadingsWidget'
import { SensorChartWidget } from '@/components/dashboard/widgets/SensorChartWidget'
import { WeatherWidget } from '@/components/dashboard/widgets/WeatherWidget'
import { RecentCommandsWidget } from '@/components/dashboard/widgets/RecentCommandsWidget'
import { ActiveNotificationsWidget } from '@/components/dashboard/widgets/ActiveNotificationsWidget'
import type { Farm } from '@/types/api'

export default async function FarmDashboardPage({
  params,
}: {
  params: Promise<{ farmId: string }>
}) {
  const { farmId } = await params
  const farm = await serverFetch<Farm>(`/farms/${farmId}/`)

  return (
    <div className="space-y-6">
      {/* WebSocket canlı veri senkronizasyonu — görünmez */}
      <FarmLiveDataSync farmId={farmId} />

      <div>
        <h1 className="text-2xl font-semibold text-slate-800">{farm?.name ?? 'Çiftlik Özeti'}</h1>
        {farm?.location && <p className="mt-0.5 text-sm text-slate-500">{farm.location}</p>}
      </div>

      {/* Güncel ölçümler — tam genişlik */}
      <CurrentReadingsWidget farmId={farmId} />

      {/* Zaman serisi grafiği — tam genişlik */}
      <SensorChartWidget farmId={farmId} />

      {/* Alt satır — 3 widget yan yana */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <WeatherWidget farmId={farmId} />
        <RecentCommandsWidget farmId={farmId} />
        <ActiveNotificationsWidget farmId={farmId} />
      </div>
    </div>
  )
}
