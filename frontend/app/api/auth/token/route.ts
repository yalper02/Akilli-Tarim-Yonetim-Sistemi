import { cookies } from 'next/headers'

/** İstemci bileşenlerinin WebSocket bağlantısı için erişim tokenını okumasını sağlar. */
export async function GET() {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value
  if (!token) {
    return Response.json({ detail: 'Oturum açılmamış.' }, { status: 401 })
  }
  return Response.json({ access_token: token })
}
