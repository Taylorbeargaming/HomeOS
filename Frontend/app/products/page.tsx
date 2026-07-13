import Layout from "../../components/layout";
import { getProducts } from "../../lib/api";

export default async function ProductsPage() {
    const products = await getProducts();

    return (
        <Layout title="Products">
            <table className="w-full border-collapse border border-gray-300">
                <thead>
                    <tr className="bg-gray-200 text-black">
                        <th className="border p-2">ID</th>
                        <th className="border p-2">Product</th>
                        <th className="border p-2">Unit</th>
                        <th className="border p-2">Active</th>
                    </tr>
                </thead>

                <tbody>
                    {products.map((product: any) => (
                        <tr key={product.product_id}>
                            <td className="border p-2">{product.product_id}</td>
                            <td className="border p-2">{product.product_name}</td>
                            <td className="border p-2">{product.unit_id}</td>
                            <td className="border p-2">
                                {product.is_active ? "Yes" : "No"}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </Layout>
    );
}