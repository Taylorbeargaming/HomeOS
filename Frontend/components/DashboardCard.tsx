type DashboardCardProps = {
  title: string;
  icon: string;
};

export default function DashboardCard({
  title,
  icon,
}: DashboardCardProps) {
  return (
    <button className="bg-black rounded-xl shadow p-8 text-left hover:shadow-lg transition w-full">
      <div className="text-4xl mb-4">{icon}</div>

      <h2 className="text-2xl font-semibold">
        {title}
      </h2>
    </button>
  );
}