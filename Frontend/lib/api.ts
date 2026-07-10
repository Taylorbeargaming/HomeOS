const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export async function getHealth() {
    const response = await fetch(`${API_URL}/health`);

    if (!response.ok) {
        throw new Error("Backend unavailable");
    }

    return response.json();
}