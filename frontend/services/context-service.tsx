export async function fetchContextSnapshot(sessionId: string) {
    if (!sessionId) throw new Error("No session ID provided");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/skincare-gpt/context-snapshot?session_id=${sessionId}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    });

    if (response.status === 404) throw new Error("Context not found");
    if (!response.body) throw new Error("No response body");

    return await response.json();
}

export function getNewSessionId() {
    return fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/skincare-gpt/new-session`, {
        method: "GET",
        credentials: "include",
    }).then((response) => response.json());
}

export async function resetContext(sessionId: string) {
    if (!sessionId) throw new Error("No session ID provided");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/skincare-gpt/reset-context?session_id=${sessionId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
    });
    return response.json();
}