import DashboardCard from "../components/DashboardCard";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-10">
      <div className="max-w-6xl mx-auto">

        <h1 className="text-5xl font-bold mb-10" style={{ color: 'black' }}>
          HomeOS
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          <DashboardCard title="Kitchen Inventory" icon="📦" />
          <DashboardCard title="Household Inventory" icon="🏠" />
          <DashboardCard title="Shopping Lists" icon="🛒" />
          <DashboardCard title="Calendar" icon="📅" />
          <DashboardCard title="Finances" icon="💷" />
          <DashboardCard title="Settings" icon="⚙️" />

        </div>
      </div>
    </main>
  );
}