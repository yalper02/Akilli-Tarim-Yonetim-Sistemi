export default async function ReportsPage({ params }: { params: Promise<{ farmId: string }> }) {
  await params
  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800">Raporlar</h1>
      <p className="mt-2 text-slate-500">Dışa aktarma ve raporlar Sprint 6&apos;da gelecek.</p>
    </div>
  )
}
