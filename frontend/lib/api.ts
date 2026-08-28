const baseUrl =
    process.env.NEXT_PUBLIC_API_URL ||
    'http://localhost:3001';

export function getToken() {
    if (typeof window === 'undefined') {
        return null;
    }

    return localStorage.getItem(
        'tripwise_token',
    );
}

export function saveToken(token: string) {
    localStorage.setItem(
        'tripwise_token',
        token,
    );
}

export function clearToken() {
    localStorage.removeItem(
        'tripwise_token',
    );
}

export async function api(
    path: string,
    options: RequestInit = {},
) {
    const token = getToken();

    const response = await fetch(
        `${baseUrl}${path}`,
        {
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
        },
    );

    if (response.status === 401) {
        clearToken();
    }

    if (!response.ok) {
        const message = await response.text();

        throw new Error(
            message || 'Request failed',
        );
    }

    return response.json();
}
