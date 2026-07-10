import DashboardCard from "./DashboardCard";

type LayoutProps = {
  title: string;
  children: React.ReactNode;
};

export default function Layout({ title, children }: LayoutProps) {
  return (
    <main className="min-h-screen bg-gray-100 p-10">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">{title}</h1>

        {children}
      </div>

      <DashboardCard title="Home" icon="🏠" href="/" />
    </main>
  );
}
