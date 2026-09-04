const baseUrl =
    process.env.NEXT_PUBLIC_API_URL ||
    'http://localhost:3001';

export function getToken() {
    if (typeof window === 'undefined') {
        return null;
    }

    return localStorage.getItem('tripwise_token');
}

export function saveToken(token: string) {
    localStorage.setItem('tripwise_token', token);
}

export function clearToken() {
    localStorage.removeItem('tripwise_token');
}

export async function api(
    path: string,
    options: RequestInit = {},
) {
    const token = getToken();

    let response: Response;

    try {
        response = await fetch(`${baseUrl}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token
                    ? {
                          Authorization: `Bearer ${token}`,
                      }
                    : {}),
                ...(options.headers || {}),
            },
        });
    } catch {
        throw new Error(
            'Unable to connect to the TripWise server. Please try again in a moment.',
        );
    }

    if (response.status === 401) {
        clearToken();
    }

    if (!response.ok) {
        const contentType = response.headers.get('content-type') || '';
        let message = '';

        if (contentType.includes('application/json')) {
            try {
                const body = await response.json();
                message =
                    typeof body?.detail === 'string'
                        ? body.detail
                        : typeof body?.message === 'string'
                          ? body.message
                          : '';
            } catch {
                message = '';
            }
        }

        if (!message) {
            try {
                message = await response.text();
            } catch {
                message = '';
            }
        }

        throw new Error(message || 'Request failed. Please try again.');
    }

    return response.json();
}
