import type { LucideIcon } from "lucide-react";
import { AlertCircle, Loader2 } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import type { SessionStatus } from "../types";
import { Badge } from "./ui/badge";
import { Card } from "./ui/card";

export { Button } from "./ui/button";
export { Card } from "./ui/card";

const statusStyles: Record<SessionStatus, { label: string; className: string }> = {
  not_started: { label: "Not started", className: "border-zinc-200 bg-zinc-50 text-zinc-500" },
  in_progress: { label: "In progress", className: "border-indigo-200 bg-indigo-50 text-indigo-700" },
  completed: { label: "Completed", className: "border-emerald-200 bg-emerald-50 text-emerald-700" },
  skipped: { label: "Skipped", className: "border-zinc-200 bg-white text-zinc-400" },
};

export function StatusBadge({ status }: { status: SessionStatus }) {
  const style = statusStyles[status];
  return (
    <Badge
      variant="outline"
      className={cn("shrink-0 rounded-full px-2 py-0.5 text-xs font-medium", style.className)}
    >
      {style.label}
    </Badge>
  );
}

export function ProgressBar({
  value,
  className,
  barClassName,
}: {
  value: number;
  className?: string;
  barClassName?: string;
}) {
  const width = Math.min(100, Math.max(0, value));
  return (
    <div className={cn("h-1.5 w-full overflow-hidden rounded-full bg-zinc-100", className)}>
      <div
        className={cn("h-full rounded-full bg-zinc-900 transition-[width] duration-300", barClassName)}
        style={{ width: `${width}%` }}
      />
    </div>
  );
}

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  hint?: string;
  icon?: LucideIcon;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</p>
        {Icon ? <Icon className="h-4 w-4 text-zinc-400" aria-hidden /> : null}
      </div>
      <p className="mt-2 text-2xl font-semibold tracking-tight text-zinc-900">{value}</p>
      {hint ? <p className="mt-0.5 text-xs text-zinc-500">{hint}</p> : null}
    </Card>
  );
}

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">{title}</h1>
        {description ? <p className="mt-1 text-sm text-zinc-500">{description}</p> : null}
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </header>
  );
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-sm text-zinc-500">
      <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
      {label}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      <p>{message}</p>
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="rounded-xl border border-dashed border-zinc-200 bg-white px-6 py-12 text-center">
      <p className="text-sm font-medium text-zinc-700">{title}</p>
      {description ? <p className="mt-1 text-sm text-zinc-500">{description}</p> : null}
    </div>
  );
}
