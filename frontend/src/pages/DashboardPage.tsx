import { ArrowRight, BookOpen, CheckCircle2, CircleDot, Clock, Layers } from "lucide-react";
import { Link } from "react-router-dom";

import {
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  ProgressBar,
  StatCard,
  StatusBadge,
} from "../components/ui";
import { useDashboard } from "../hooks/queries";
import { formatDateTime, formatHours, formatMinutes, formatPercent } from "../lib/format";

export function DashboardPage() {
  const { data, isPending, isError, error } = useDashboard();

  if (isPending) return <LoadingState label="Loading dashboard…" />;
  if (isError) return <ErrorState message={error.message} />;

  const next = data.next_session;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="One session at a time. Here is where you are in the 16-week curriculum."
      />

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                Overall progress
              </p>
              <p className="mt-2 text-4xl font-semibold tracking-tight text-zinc-900">
                {formatPercent(data.overall.progress_percent)}
              </p>
              <p className="mt-1 text-sm text-zinc-500">
                {data.overall.completed_sessions} of {data.overall.total_sessions} sessions completed
              </p>
            </div>
            <div className="rounded-lg border border-zinc-200 px-3 py-2 text-right">
              <p className="text-xs text-zinc-500">Phases</p>
              <p className="text-sm font-semibold text-zinc-900">
                {data.overall.completed_phases} / {data.overall.total_phases}
              </p>
            </div>
          </div>
          <ProgressBar value={data.overall.progress_percent} className="mt-5" />
          <div className="mt-4 flex flex-wrap gap-x-6 gap-y-1 text-sm text-zinc-500">
            <span>{formatHours(data.overall.total_learning_minutes)} learned</span>
            <span>{data.counts.completed} completed</span>
            <span>{data.counts.in_progress} in progress</span>
            {data.counts.skipped > 0 ? <span>{data.counts.skipped} skipped</span> : null}
          </div>
          {data.curriculum_completed ? (
            <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              Curriculum completed. Nice work finishing all {data.overall.total_sessions} sessions.
            </p>
          ) : null}
        </Card>

        <div className="grid grid-cols-2 gap-3 lg:col-span-2">
          <StatCard
            label="Learning hours"
            value={formatHours(data.overall.total_learning_minutes)}
            hint="Actual time recorded"
            icon={Clock}
          />
          <StatCard
            label="Completed"
            value={data.counts.completed}
            hint={`of ${data.counts.total} sessions`}
            icon={CheckCircle2}
          />
          <StatCard
            label="In progress"
            value={data.counts.in_progress}
            hint="Started, not finished"
            icon={CircleDot}
          />
          <StatCard
            label="Not started"
            value={data.counts.not_started}
            hint={data.counts.skipped > 0 ? `${data.counts.skipped} skipped` : "Still ahead"}
            icon={Layers}
          />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
              Current learning phase
            </p>
            {data.current_phase ? (
              <Link
                to="/curriculum"
                className="text-xs font-medium text-zinc-500 hover:text-zinc-900"
              >
                View curriculum
              </Link>
            ) : null}
          </div>
          {data.current_phase ? (
            <div className="mt-3">
              <p className="text-xs text-zinc-500">Week {data.current_phase.week_number}</p>
              <h2 className="mt-0.5 text-lg font-semibold tracking-tight text-zinc-900">
                {data.current_phase.title}
              </h2>
              <div className="mt-3 flex items-center gap-3">
                <ProgressBar value={data.current_phase.progress_percent} className="flex-1" />
                <span className="text-xs tabular-nums text-zinc-500">
                  {data.current_phase.completed_sessions}/{data.current_phase.total_sessions}
                </span>
              </div>
              {data.current_phase.next_session ? (
                <div className="mt-4 rounded-lg border border-zinc-200 bg-zinc-50 p-3">
                  <p className="text-xs text-zinc-500">Up next</p>
                  <p className="mt-0.5 text-sm font-medium text-zinc-900">
                    {data.current_phase.next_session.title}
                  </p>
                  <Link
                    to={`/sessions/${data.current_phase.next_session.id}`}
                    className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700"
                  >
                    Open session <ArrowRight className="h-3.5 w-3.5" aria-hidden />
                  </Link>
                </div>
              ) : null}
            </div>
          ) : (
            <EmptyState
              title={data.curriculum_completed ? "Curriculum completed" : "No active session"}
              description={
                data.curriculum_completed
                  ? "Every session is completed."
                  : "Reset or start a session to continue."
              }
            />
          )}
        </Card>

        <Card>
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            Next learning session
          </p>
          {next ? (
            <div className="mt-3">
              <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                <span>
                  Week {next.week_number} · Session {next.session_number}
                </span>
                <StatusBadge status={next.status} />
              </div>
              <Link
                to={`/sessions/${next.id}`}
                className="mt-2 block text-lg font-semibold tracking-tight text-zinc-900 hover:text-indigo-700"
              >
                {next.title}
              </Link>
              <div className="mt-3 space-y-2 text-sm">
                <div>
                  <p className="text-xs font-medium text-zinc-500">Target</p>
                  <p className="text-zinc-700">{next.learning_objectives[0] ?? "—"}</p>
                </div>
                <div className="flex items-center gap-2 text-zinc-500">
                  <Clock className="h-3.5 w-3.5" aria-hidden />
                  <span>{formatMinutes(next.estimated_duration_minutes)} estimated</span>
                </div>
              </div>
              <Link
                to={`/sessions/${next.id}`}
                className="mt-4 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-zinc-900 px-3.5 py-2 text-sm font-medium text-white hover:bg-zinc-800"
              >
                <BookOpen className="h-4 w-4" aria-hidden />
                Go to session
              </Link>
            </div>
          ) : (
            <EmptyState title="No session queued" description="Everything is completed or skipped." />
          )}
        </Card>
      </div>

      <Card>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            Recent activity
          </p>
          <Link to="/history" className="text-xs font-medium text-zinc-500 hover:text-zinc-900">
            View history
          </Link>
        </div>
        {data.recent_activity.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="No completed sessions yet"
              description="Start your first session to see activity here."
            />
          </div>
        ) : (
          <ul className="mt-3 divide-y divide-zinc-100">
            {data.recent_activity.map((item) => (
              <li key={item.session_id} className="flex items-center justify-between gap-4 py-3">
                <div className="min-w-0">
                  <Link
                    to={`/sessions/${item.session_id}`}
                    className="block truncate text-sm font-medium text-zinc-900 hover:text-indigo-700"
                  >
                    {item.title}
                  </Link>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    Week {item.week_number} · {formatDateTime(item.completed_at)}
                  </p>
                </div>
                <span className="shrink-0 text-xs tabular-nums text-zinc-500">
                  {formatMinutes(item.actual_duration_minutes)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
