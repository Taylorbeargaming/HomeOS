const API_URL = process.env.NEXT_PUBLIC_API_URL!;

async function fetchAPI(endpoint: string) {
    const response = await fetch(`${API_URL}${endpoint}`);

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
}

export function getHealth() {
    return fetchAPI("/health");
}

export function getDashboard() {
    return fetchAPI("/dashboard");
}

export function getProducts() {
    return fetchAPI("/products");
}