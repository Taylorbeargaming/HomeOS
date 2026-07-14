import DashboardCard from "../components/DashboardCard";
import BackendStatus from "../components/BackendStatus";
import { getDashboard } from "../lib/api";

export default async function Home() {
  const dashboard = await getDashboard();

  return (
    <>
      <BackendStatus />

      <main className="min-h-screen bg-gray-100 p-10">
        <div className="max-w-6xl mx-auto">

          <h1 className="text-5xl font-bold mb-10" style={{ color: "black" }}>
            HomeOS
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

            <DashboardCard
              title={`Kitchen Inventory (${dashboard.inventory})`}
              icon="📦"
              href="/kitchen"
            />

            <DashboardCard
              title={`Shopping Lists (${dashboard.shopping_lists})`}
              icon="🛒"
              href="/shopping"
            />

            <DashboardCard
              title={`Recipes (${dashboard.recipes})`}
              icon="🍽️"
              href="/recipes"
            />

            <DashboardCard
              title="Household Tasks"
              icon="✅"
              href="/tasks"
            />

            <DashboardCard
              title="Calendar"
              icon="📅"
              href="/calendar"
            />

            <DashboardCard
              title="Settings"
              icon="⚙️"
              href="/settings"
            />
            

          </div>
        </div>
      </main>
    </>
  );
}