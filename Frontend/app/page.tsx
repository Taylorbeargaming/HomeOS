import DashboardCard from "../components/DashboardCard";
import { getHealth } from "../lib/api";
import BackendStatus from "../components/BackendStatus";


export default  function Home() {

  return (

    <> <BackendStatus />

    
    <main className="min-h-screen bg-gray-100 p-10">
      <div className="max-w-6xl mx-auto">

        <h1 className="text-5xl font-bold mb-10" style={{ color: 'black' }}>
          HomeOS
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          <DashboardCard title="Kitchen Inventory" icon="📦" href="/kitchen" />
          <DashboardCard title="Household Inventory" icon="🏠" href="/household" />
          <DashboardCard title="Shopping Lists" icon="🛒" href="/shopping" />
          <DashboardCard title="Calendar" icon="📅" href="/calendar" />
          <DashboardCard title="Finances" icon="💷" href="/finances" />
          <DashboardCard title="Settings" icon="⚙️" href="/settings" />

        </div>
      </div>
    </main>

  </>
  );
}