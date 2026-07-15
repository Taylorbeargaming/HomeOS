const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error(
    "NEXT_PUBLIC_API_URL is not configured. Add it to Frontend/.env.local."
  );
}

export type HealthResponse = {
  status: string;
};

export type DashboardResponse = {
  inventory: number;
  shopping_lists: number;
  recipes: number;
};

export type Unit = {
  unit_id: number;
  unit_name: string;
  abbreviation: string;
  is_active: boolean;
};

export type Product = {
  product_id: number;
  product_name: string;
  notes: string | null;
  is_active: boolean;
  unit_id: number;
  unit_name: string;
};

export type InventoryItem = {
  inventory_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_id: number;
  unit_name: string;
};

export type InventoryTransactionType =
  | "Purchase"
  | "Consumption"
  | "Waste"
  | "Adjustment"
  | "TransferIn"
  | "TransferOut"
  | "InitialStock";

export type InventoryTransaction = {
  transaction_id: string;
  inventory_id: number;
  quantity_change: number;
  transaction_type: InventoryTransactionType;
  notes: string | null;
  transaction_date: string;
};

export type CreateProductInput = {
  product_name: string;
  unit_id: number;
  notes?: string | null;
};

export type CreateInventoryItemInput = {
  product_id: number;
  quantity: number;
};

export type CreateInventoryTransactionInput = {
  inventory_id: number;
  quantity_change: number;
  transaction_type: InventoryTransactionType;
  notes?: string | null;
  transaction_date?: string | null;
};

type APIErrorResponse = {
  detail?: string;
};

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = `API request failed with status ${response.status}`;

    try {
      const errorBody = (await response.json()) as APIErrorResponse;

      if (errorBody.detail) {
        message = errorBody.detail;
      }
    } catch {
      // Keep the fallback message if the API response is not JSON.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return fetchAPI<HealthResponse>("/health");
}

export function getDashboard(): Promise<DashboardResponse> {
  return fetchAPI<DashboardResponse>("/dashboard");
}

export function getUnits(): Promise<Unit[]> {
  return fetchAPI<Unit[]>("/units");
}

export function getProducts(): Promise<Product[]> {
  return fetchAPI<Product[]>("/products");
}

export function createProduct(
  input: CreateProductInput
): Promise<Product> {
  return fetchAPI<Product>("/products", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getInventory(): Promise<InventoryItem[]> {
  return fetchAPI<InventoryItem[]>("/inventory");
}

export function createInventoryItem(
  input: CreateInventoryItemInput
): Promise<InventoryItem> {
  return fetchAPI<InventoryItem>("/inventory", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function createInventoryTransaction(
  input: CreateInventoryTransactionInput
): Promise<InventoryTransaction> {
  return fetchAPI<InventoryTransaction>("/inventory-transactions", {
    method: "POST",
    body: JSON.stringify(input),
  });
}