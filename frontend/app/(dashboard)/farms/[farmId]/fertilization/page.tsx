export default async function FertilizationPage({
  params,
}: {
  params: Promise<{ farmId: string }>
}) {
  await params
  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800">Gübreleme</h1>
      <p className="mt-2 text-slate-500">Gübreleme önerileri Sprint 6&apos;da gelecek.</p>
    </div>
  )
}
