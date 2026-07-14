import Layout from "../../components/layout";
import Button from "../../components/button";
import { getInventory } from "../../lib/api";

export default async function KitchenPage() {
    const inventory = await getInventory();

    return (
        <Layout title="Kitchen Inventory">

            <div className="flex justify-end mb-6">
                <Button>
                    + Add Item
                </Button>
            </div>

            <table className="w-full border border-gray-300 border-collapse">
                <thead>
                    <tr className="bg-gray-200 text-black">
                        <th className="border p-2">Product</th>
                        <th className="border p-2">Quantity</th>
                        <th className="border p-2">Unit</th>
                        <th className="border p-2">Actions</th>
                    </tr>
                </thead>

                <tbody>
                    {inventory.map((item: any) => (
                        <tr key={item.inventory_id}>
                            <td className="border p-2">{item.product_name}</td>
                            <td className="border p-2">{item.quantity}</td>
                            <td className="border p-2">{item.unit_name}</td>
                            <td className="border p-2">
                                <div className="flex gap-2">
                                    <Button>Edit</Button>
                                    <Button>Delete</Button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

        </Layout>
    );
}