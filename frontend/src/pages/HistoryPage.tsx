import { FilterX } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  StatusBadge,
} from "../components/ui";
import { useHistory } from "../hooks/queries";
import { formatDate, formatMinutes } from "../lib/format";
import type { HistoryFilters, SessionStatus } from "../types";

const STATUS_OPTIONS: Array<{ value: SessionStatus; label: string }> = [
  { value: "not_started", label: "Not started" },
  { value: "in_progress", label: "In progress" },
  { value: "completed", label: "Completed" },
  { value: "skipped", label: "Skipped" },
];

const selectClassName =
  "flex h-9 w-full rounded-lg border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50";

export function HistoryPage() {
  const [week, setWeek] = useState("");
  const [status, setStatus] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const filters: HistoryFilters = {
    week: week ? Number(week) : undefined,
    status: status ? (status as SessionStatus) : undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  };
  const { data, isPending, isError, error } = useHistory(filters);

  const hasFilters = Boolean(week || status || dateFrom || dateTo);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Learning History"
        description="Every session you have started, completed, or skipped."
      />

      <Card>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-1.5">
            <Label
              htmlFor="history-week"
              className="text-xs font-medium uppercase tracking-wide text-zinc-500"
            >
              Week
            </Label>
            <select
              id="history-week"
              value={week}
              onChange={(event) => setWeek(event.target.value)}
              className={selectClassName}
            >
              <option value="">All weeks</option>
              {Array.from({ length: 16 }, (_, index) => index + 1).map((value) => (
                <option key={value} value={value}>
                  Week {value}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <Label
              htmlFor="history-status"
              className="text-xs font-medium uppercase tracking-wide text-zinc-500"
            >
              Status
            </Label>
            <select
              id="history-status"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              className={selectClassName}
            >
              <option value="">All statuses</option>
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <Label
              htmlFor="history-from"
              className="text-xs font-medium uppercase tracking-wide text-zinc-500"
            >
              From
            </Label>
            <Input
              id="history-from"
              type="date"
              value={dateFrom}
              onChange={(event) => setDateFrom(event.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <Label
              htmlFor="history-to"
              className="text-xs font-medium uppercase tracking-wide text-zinc-500"
            >
              To
            </Label>
            <Input
              id="history-to"
              type="date"
              value={dateTo}
              onChange={(event) => setDateTo(event.target.value)}
            />
          </div>
        </div>

        {hasFilters ? (
          <div className="mt-3">
            <Button
              variant="ghost"
              size="sm"
              className="text-xs"
              onClick={() => {
                setWeek("");
                setStatus("");
                setDateFrom("");
                setDateTo("");
              }}
            >
              <FilterX className="h-3.5 w-3.5" aria-hidden />
              Clear filters
            </Button>
          </div>
        ) : null}
      </Card>

      {isPending ? <LoadingState label="Loading history…" /> : null}
      {isError ? <ErrorState message={error.message} /> : null}

      {data ? (
        <Card className="p-0">
          <div className="flex items-center justify-between border-b border-zinc-100 px-5 py-3">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Sessions</p>
            <p className="text-xs text-zinc-500">{data.length} shown</p>
          </div>
          {data.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="No sessions match these filters"
                description="Try a different week, status, or date range."
              />
            </div>
          ) : (
            <ul className="divide-y divide-zinc-100">
              {data.map((item) => (
                <li key={item.session_id} className="px-5 py-3.5">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
                    <div className="flex min-w-0 gap-4">
                      <div className="w-24 shrink-0 pt-0.5 text-xs text-zinc-500">
                        {formatDate(item.activity_at)}
                      </div>
                      <div className="min-w-0">
                        <Link
                          to={`/sessions/${item.session_id}`}
                          className="block text-sm font-medium text-zinc-900 hover:text-indigo-700"
                        >
                          {item.title}
                        </Link>
                        <p className="mt-0.5 text-xs text-zinc-500">
                          Week {item.week_number} · {item.phase_title}
                        </p>
                        {item.note_excerpt ? (
                          <p className="mt-1 line-clamp-2 text-xs text-zinc-500">{item.note_excerpt}</p>
                        ) : null}
                      </div>
                    </div>
                    <div className="flex shrink-0 items-center gap-3 pl-28 sm:pl-0">
                      <span className="text-xs tabular-nums text-zinc-500">
                        {formatMinutes(item.actual_duration_minutes)}
                      </span>
                      <StatusBadge status={item.status} />
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      ) : null}
    </div>
  );
}
