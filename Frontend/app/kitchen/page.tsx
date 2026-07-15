import Layout from "../../components/layout";
import KitchenInventoryClient from "../../components/KitchenInventoryClient";
import { getInventory } from "../../lib/api";

export default async function KitchenPage() {
  const inventory = await getInventory();

  return (
    <Layout title="Kitchen Inventory">
      <KitchenInventoryClient inventory={inventory} />
    </Layout>
  );
}