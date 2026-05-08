/** İstemci bileşenlerinden Django API'sine proxy üzerinden istek atar. */
export async function clientFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`/api/backend${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${path}`)
  }
  return res.json() as Promise<T>
}
