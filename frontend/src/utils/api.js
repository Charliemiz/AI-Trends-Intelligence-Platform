const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://example.com/api'

export async function apiRequest(path, options = {}) {
    const { headers = {}, ...rest } = options

    const response = await fetch(`${BASE_URL}${path}`, {
        headers: {
            'Content-Type': 'application/json',
            ...headers, 
        },
        ...rest, 
    })

    if (!response.ok) {
        const message = await response.text()
        throw new Error(`HTTP ${response.status}: ${message}`)
    }

    const contentType = response.headers.get('content-type') || ''
    return contentType.includes('application/json')
        ? response.json()
        : response.text()
}
