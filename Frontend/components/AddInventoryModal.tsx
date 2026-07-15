"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  createInventoryItem,
  getProducts,
  Product,
} from "../lib/api";

type AddInventoryModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function AddInventoryModal({
  isOpen,
  onClose,
}: AddInventoryModalProps) {
  const router = useRouter();

  const [products, setProducts] = useState<Product[]>([]);
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    async function loadProducts() {
      setIsLoadingProducts(true);
      setError(null);

      try {
        const productList = await getProducts();

        setProducts(
          productList.filter((product) => product.is_active)
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load products."
        );
      } finally {
        setIsLoadingProducts(false);
      }
    }

    void loadProducts();
  }, [isOpen]);

  function resetForm() {
    setProductId("");
    setQuantity("");
    setError(null);
  }

  function handleClose() {
    if (isSubmitting) {
      return;
    }

    resetForm();
    onClose();
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const parsedProductId = Number(productId);
    const parsedQuantity = Number(quantity);

    if (!parsedProductId) {
      setError("Select a product.");
      return;
    }

    if (!Number.isFinite(parsedQuantity) || parsedQuantity <= 0) {
      setError("Quantity must be greater than zero.");
      return;
    }

    setIsSubmitting(true);

    try {
      await createInventoryItem({
        product_id: parsedProductId,
        quantity: parsedQuantity,
      });

      resetForm();
      onClose();
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to add inventory item."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="presentation"
      onMouseDown={handleClose}
    >
      <div
        className="w-full max-w-md rounded-xl bg-white p-6 shadow-lg"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-inventory-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <h2
          id="add-inventory-title"
          className="mb-6 text-2xl font-bold text-black"
        >
          Add Inventory Item
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="product"
              className="mb-2 block font-medium text-black"
            >
              Product
            </label>

            <select
              id="product"
              value={productId}
              onChange={(event) => setProductId(event.target.value)}
              disabled={isLoadingProducts || isSubmitting}
              className="w-full rounded border border-gray-300 px-3 py-2 text-black"
            >
              <option value="">
                {isLoadingProducts
                  ? "Loading products..."
                  : "Select a product"}
              </option>

              {products.map((product) => (
                <option
                  key={product.product_id}
                  value={product.product_id}
                >
                  {product.product_name} ({product.unit_name})
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label
              htmlFor="quantity"
              className="mb-2 block font-medium text-black"
            >
              Starting quantity
            </label>

            <input
              id="quantity"
              type="number"
              min="0.001"
              step="0.001"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
              disabled={isSubmitting}
              className="w-full rounded border border-gray-300 px-3 py-2 text-black"
              placeholder="Enter quantity"
            />
          </div>

          {error && (
            <div
              className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700"
              role="alert"
            >
              {error}
            </div>
          )}

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="rounded bg-gray-500 px-4 py-2 text-white disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={
                isSubmitting ||
                isLoadingProducts ||
                products.length === 0
              }
              className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
            >
              {isSubmitting ? "Adding..." : "Add Item"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}