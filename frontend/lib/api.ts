const baseUrl =
    process.env.NEXT_PUBLIC_API_URL ||
    'http://localhost:3001';

export async function api(
    path: string,
    options: RequestInit = {},
) {
    const response = await fetch(
        `${baseUrl}${path}`,
        {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {}),
            },
        },
    );

    if (!response.ok) {
        const message = await response.text();

        throw new Error(
            message || 'Request failed',
        );
    }

    return response.json();
}