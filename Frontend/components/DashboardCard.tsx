type DashboardCardProps = {
  title: string;
  icon: string;
  href: string;
};

import Link from "next/link";
export default function DashboardCard({
  title,
  icon,
  href,
}: DashboardCardProps) {
  return (
    <Link href={href}>
      <div className="bg-black rounded-xl shadow p-8 hover:shadow-lg transition cursor-pointer">
        <div className="text-4xl mb-4">{icon}</div>
        <h2 className="text-2xl font-semibold">{title}</h2>
      </div>
    </Link>
  );
}