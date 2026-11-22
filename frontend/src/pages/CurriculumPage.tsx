import { CheckCircle2, Circle, CircleDot, MinusCircle } from "lucide-react";
import { Link } from "react-router-dom";

import { Card, ErrorState, LoadingState, PageHeader, ProgressBar, StatusBadge } from "../components/ui";
import { usePhases } from "../hooks/queries";
import type { Session, SessionStatus } from "../types";
import { formatMinutes, formatPercent } from "../lib/format";

function SessionStatusIcon({ status }: { status: SessionStatus }) {
  if (status === "completed") {
    return <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" aria-hidden />;
  }
  if (status === "in_progress") {
    return <CircleDot className="h-4 w-4 shrink-0 text-indigo-500" aria-hidden />;
  }
  if (status === "skipped") {
    return <MinusCircle className="h-4 w-4 shrink-0 text-zinc-300" aria-hidden />;
  }
  return <Circle className="h-4 w-4 shrink-0 text-zinc-300" aria-hidden />;
}

function isFinal(status: SessionStatus): boolean {
  return status === "completed" || status === "skipped";
}

export function CurriculumPage() {
  const { data: phases, isPending, isError, error } = usePhases();

  if (isPending) return <LoadingState label="Loading curriculum…" />;
  if (isError) return <ErrorState message={error.message} />;

  const allSessions: Session[] = phases.flatMap((phase) => phase.sessions);
  const completed = allSessions.filter((session) => session.status === "completed").length;
  const nextSessionId = allSessions.find((session) => !isFinal(session.status))?.id;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Curriculum"
        description="The original 22-topic course grouped into 16 weeks — each advancing one product: NoteVault."
        actions={
          <div className="text-right">
            <p className="text-sm font-medium tabular-nums text-zinc-900">
              {completed} / {allSessions.length}
            </p>
            <p className="text-xs text-zinc-500">sessions completed</p>
          </div>
        }
      />

      <div className="space-y-4">
        {phases.map((phase) => (
          <Card key={phase.id} className="overflow-hidden p-0">
            <div className="border-b border-zinc-100 px-5 py-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                    Week {phase.week_number}
                  </p>
                  <h2 className="mt-0.5 text-base font-semibold tracking-tight text-zinc-900">
                    {phase.title}
                  </h2>
                  <p className="mt-1 max-w-2xl text-sm text-zinc-500">{phase.description}</p>
                </div>
                <div className="shrink-0 text-right">
                  <p className="text-sm font-medium tabular-nums text-zinc-700">
                    {formatPercent(phase.progress_percent)}
                  </p>
                  <p className="text-xs text-zinc-500">
                    {phase.completed_sessions} / {phase.total_sessions} sessions
                  </p>
                </div>
              </div>
              <ProgressBar value={phase.progress_percent} className="mt-3" />
            </div>

            <ul className="divide-y divide-zinc-100">
              {phase.sessions.map((session) => (
                <li key={session.id}>
                  <Link
                    to={`/sessions/${session.id}`}
                    className="flex items-center gap-3 px-5 py-3 transition-colors hover:bg-zinc-50"
                  >
                    <SessionStatusIcon status={session.status} />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-medium text-zinc-800">{session.title}</p>
                        {session.id === nextSessionId ? (
                          <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-[11px] font-medium text-indigo-700">
                            Up next
                          </span>
                        ) : null}
                      </div>
                      <p className="mt-0.5 text-xs text-zinc-500">
                        Session {session.order_index} · {formatMinutes(session.estimated_duration_minutes)}
                      </p>
                    </div>
                    <StatusBadge status={session.status} />
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
}
