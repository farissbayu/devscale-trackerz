import { BarChart3, BookOpen, Flag, History, LayoutDashboard } from "lucide-react";
import { useEffect } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { cn } from "@/lib/utils";

const navigation = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/curriculum", label: "Curriculum", icon: BookOpen, end: false },
  { to: "/history", label: "History", icon: History, end: false },
  { to: "/progress", label: "Progress", icon: BarChart3, end: false },
];

const titles: Record<string, string> = {
  "/": "Dashboard",
  "/curriculum": "Curriculum",
  "/history": "Learning History",
  "/progress": "Progress",
};

function Brand() {
  return (
    <div className="flex items-center gap-2.5">
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-zinc-900 text-white">
        <Flag className="h-4 w-4" aria-hidden />
      </span>
      <div className="leading-tight">
        <p className="text-sm font-semibold tracking-tight text-zinc-900">Finishline</p>
        <p className="text-[11px] text-zinc-500">One session at a time.</p>
      </div>
    </div>
  );
}

function SidebarLink({
  to,
  label,
  icon: Icon,
  end,
}: {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  end: boolean;
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
          isActive ? "bg-zinc-100 text-zinc-900" : "text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900",
        )
      }
    >
      <Icon className="h-4 w-4" aria-hidden />
      {label}
    </NavLink>
  );
}

export function Layout() {
  const location = useLocation();

  useEffect(() => {
    const key = location.pathname.startsWith("/sessions") ? "/curriculum" : location.pathname;
    document.title = `${titles[key] ?? "Finishline"} · Finishline`;
  }, [location.pathname]);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[232px_1fr]">
      <aside className="hidden border-r border-zinc-200 bg-white lg:flex lg:h-screen lg:flex-col lg:sticky lg:top-0">
        <div className="px-4 py-5">
          <Brand />
        </div>
        <nav className="flex flex-col gap-0.5 px-2.5">
          {navigation.map((item) => (
            <SidebarLink key={item.to} {...item} />
          ))}
        </nav>
        <div className="mt-auto px-4 py-5">
          <p className="text-xs leading-relaxed text-zinc-400">
            Devscale AI Product Engineering
            <br />
            16 weeks · 58 sessions
          </p>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col">
        <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-4 py-3 lg:hidden">
          <Brand />
        </header>

        <main className="mx-auto w-full max-w-5xl flex-1 px-4 pb-24 pt-6 sm:px-6 lg:px-10 lg:pb-12 lg:pt-10">
          <Outlet />
        </main>

        <nav className="fixed inset-x-0 bottom-0 z-10 grid grid-cols-4 border-t border-zinc-200 bg-white/95 backdrop-blur lg:hidden">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium",
                  isActive ? "text-zinc-900" : "text-zinc-400",
                )
              }
            >
              <item.icon className="h-4 w-4" aria-hidden />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}
