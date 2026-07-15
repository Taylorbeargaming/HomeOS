"use client";

import { useState } from "react";

import AddInventoryModal from "./AddInventoryModal";
import Button from "./button";
import type { InventoryItem } from "../lib/api";

type KitchenInventoryClientProps = {
  inventory: InventoryItem[];
};

export default function KitchenInventoryClient({
  inventory,
}: KitchenInventoryClientProps) {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  return (
    <>
      <div className="mb-6 flex justify-end">
        <Button onClick={() => setIsAddModalOpen(true)}>
          + Add Item
        </Button>
      </div>

      {inventory.length === 0 ? (
        <div className="rounded border border-gray-300 bg-white p-6 text-center text-gray-600">
          No inventory items have been added.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-200 text-black">
                <th className="border p-2 text-left">Product</th>
                <th className="border p-2 text-left">Quantity</th>
                <th className="border p-2 text-left">Unit</th>
                <th className="border p-2 text-left">Status</th>
                <th className="border p-2 text-left">Actions</th>
              </tr>
            </thead>

            <tbody>
              {inventory.map((item) => (
                <tr key={item.inventory_id}>
                  <td className="border p-2 text-black">
                    {item.product_name}
                  </td>

                  <td className="border p-2 text-black">
                    {item.quantity}
                  </td>

                  <td className="border p-2 text-black">
                    {item.unit_name}
                  </td>

                  <td className="border p-2">
                    {item.quantity > 0 ? (
                      <span className="font-medium text-green-700">
                        In stock
                      </span>
                    ) : (
                      <span className="font-medium text-red-700">
                        Out of stock
                      </span>
                    )}
                  </td>

                  <td className="border p-2">
                    <Button>Adjust</Button>
                  </td>
                </tr>
              ))}s
            </tbody>
          </table>
        </div>
      )}

      <AddInventoryModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />
    </>
  );
}