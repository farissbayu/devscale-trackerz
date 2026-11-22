import { Card, ErrorState, LoadingState, PageHeader, ProgressBar } from "../components/ui";
import { useProgressOverview } from "../hooks/queries";
import { formatHours, formatMinutes, formatPercent } from "../lib/format";

export function ProgressPage() {
  const { data, isPending, isError, error } = useProgressOverview();

  if (isPending) return <LoadingState label="Loading progress…" />;
  if (isError) return <ErrorState message={error.message} />;

  const minutesPerSession =
    data.completed_sessions > 0
      ? Math.round(data.total_learning_minutes / data.completed_sessions)
      : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Progress"
        description="How far you are across the whole curriculum and each week."
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="sm:col-span-2">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Overall</p>
          <div className="mt-2 flex items-end justify-between gap-4">
            <p className="text-4xl font-semibold tracking-tight text-zinc-900">
              {formatPercent(data.progress_percent)}
            </p>
            <p className="pb-1 text-sm text-zinc-500">
              {data.completed_sessions} / {data.total_sessions} sessions
            </p>
          </div>
          <ProgressBar value={data.progress_percent} className="mt-4 h-2" />
          <p className="mt-3 text-xs text-zinc-500">
            Progress counts completed sessions only. Skipped sessions are not counted as completed.
          </p>
        </Card>

        <div className="grid gap-4">
          <Card>
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
              Total learning time
            </p>
            <p className="mt-2 text-2xl font-semibold tracking-tight text-zinc-900">
              {formatHours(data.total_learning_minutes)}
            </p>
            <p className="mt-0.5 text-xs text-zinc-500">
              {formatMinutes(data.total_learning_minutes)} recorded
            </p>
          </Card>
          <Card>
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
              Avg per completed session
            </p>
            <p className="mt-2 text-2xl font-semibold tracking-tight text-zinc-900">
              {data.completed_sessions > 0 ? formatMinutes(minutesPerSession) : "—"}
            </p>
            <p className="mt-0.5 text-xs text-zinc-500">Based on actual duration</p>
          </Card>
        </div>
      </div>

      <Card className="p-0">
        <div className="border-b border-zinc-100 px-5 py-3">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Progress per week</p>
        </div>
        <ul className="divide-y divide-zinc-100">
          {data.weeks.map((week) => (
            <li key={week.week_number} className="px-5 py-3">
              <div className="flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-zinc-900">
                    <span className="mr-2 text-xs text-zinc-500">W{week.week_number}</span>
                    {week.title}
                  </p>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    {week.completed_sessions}/{week.total_sessions} sessions ·{" "}
                    {formatMinutes(week.learning_minutes)} learned
                  </p>
                </div>
                <span className="shrink-0 text-xs tabular-nums text-zinc-500">
                  {formatPercent(week.progress_percent)}
                </span>
              </div>
              <ProgressBar
                value={week.progress_percent}
                className="mt-2"
                barClassName={week.status === "completed" ? "bg-emerald-500" : undefined}
              />
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
