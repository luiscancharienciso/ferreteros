export async function apiRequest(url, options = {}) {

    const config = {
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    };

    const response = await fetch(url, config);

    if (!response.ok) {
        throw new Error("API request failed");
    }

    return response.json();
}