import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Clock,
  ExternalLink,
  Link2,
  ListChecks,
  Play,
  RotateCcw,
  Save,
  SkipForward,
} from "lucide-react";
import { useId, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Button,
  Card,
  ErrorState,
  LoadingState,
  StatusBadge,
} from "../components/ui";
import { useSession, useSessionActions } from "../hooks/queries";
import { formatDateTime, formatMinutes } from "../lib/format";
import { formatTimestamp, parseTimestamp, withTimestamp } from "../lib/video";
import type { SessionDetail } from "../types";

interface NotesState {
  what_i_learned: string;
  what_i_understand: string;
  what_i_dont_understand: string;
  implementation_notes: string;
}

function notesFromSession(session: SessionDetail): NotesState {
  return {
    what_i_learned: session.what_i_learned,
    what_i_understand: session.what_i_understand,
    what_i_dont_understand: session.what_i_dont_understand,
    implementation_notes: session.implementation_notes,
  };
}

function notesPayload(notes: NotesState) {
  return {
    what_i_learned: notes.what_i_learned,
    what_i_understand: notes.what_i_understand,
    what_i_dont_understand: notes.what_i_dont_understand,
    implementation_notes: notes.implementation_notes,
  };
}

function NotesField({
  label,
  hint,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  hint?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  const id = useId();
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      {hint ? <p className="text-xs text-muted-foreground">{hint}</p> : null}
      <Textarea
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        rows={3}
        className="resize-y"
      />
    </div>
  );
}

function CompleteDialog({
  session,
  onCancel,
  onConfirm,
  pending,
  error,
}: {
  session: SessionDetail;
  onCancel: () => void;
  onConfirm: (minutes: number) => void;
  pending: boolean;
  error: string | null;
}) {
  const fieldId = useId();
  const [minutes, setMinutes] = useState(
    String(session.actual_duration_minutes ?? session.estimated_duration_minutes),
  );
  const value = Number(minutes);
  const valid = Number.isInteger(value) && value >= 1 && value <= 1440;

  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) onCancel();
      }}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Mark session as completed</DialogTitle>
          <DialogDescription>{session.title}</DialogDescription>
        </DialogHeader>

        <form
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            if (valid) onConfirm(value);
          }}
        >
          <div className="space-y-1.5">
            <Label htmlFor={fieldId}>Actual study duration</Label>
            <Input
              id={fieldId}
              type="number"
              min={1}
              max={1440}
              step={1}
              value={minutes}
              onChange={(event) => setMinutes(event.target.value)}
              autoFocus
            />
            <p className="text-xs text-muted-foreground">
              In minutes. Your current notes will be saved with this completion.
            </p>
            {!valid ? (
              <p className="text-xs text-destructive">
                Enter a whole number between 1 and 1440.
              </p>
            ) : null}
            {error ? <p className="text-xs text-destructive">{error}</p> : null}
          </div>

          <DialogFooter className="mt-5">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={!valid || pending}>
              {pending ? "Saving…" : "Mark completed"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function SessionView({ session }: { session: SessionDetail }) {
  const actions = useSessionActions(session.id);
  const [notes, setNotes] = useState<NotesState>(() => notesFromSession(session));
  const [dialogOpen, setDialogOpen] = useState(false);
  const [sourceUrl, setSourceUrl] = useState(session.source_url);
  const sourceDirty = sourceUrl.trim() !== session.source_url;
  const [timestampInput, setTimestampInput] = useState(
    formatTimestamp(session.video_timestamp_seconds),
  );
  const [timestampError, setTimestampError] = useState<string | null>(null);
  const savedTimestamp = formatTimestamp(session.video_timestamp_seconds);
  const timestampDirty = timestampInput.trim() !== savedTimestamp;

  const savedNotes = notesFromSession(session);
  const notesDirty =
    notes.what_i_learned !== savedNotes.what_i_learned ||
    notes.what_i_understand !== savedNotes.what_i_understand ||
    notes.what_i_dont_understand !== savedNotes.what_i_dont_understand ||
    notes.implementation_notes !== savedNotes.implementation_notes;

  const actionError =
    actions.start.error?.message ??
    actions.complete.error?.message ??
    actions.saveNotes.error?.message ??
    actions.reset.error?.message ??
    actions.skip.error?.message ??
    null;

  const isCompleted = session.status === "completed";
  const isInProgress = session.status === "in_progress";

  const update = (field: keyof NotesState) => (value: string) =>
    setNotes((current) => ({ ...current, [field]: value }));

  return (
    <div className="space-y-5">
      <Link
        to="/curriculum"
        className="inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-900"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden />
        Back to curriculum
      </Link>

      <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
            <span>
              Week {session.week_number} · Session {session.order_index}
            </span>
            <span aria-hidden>·</span>
            <span>{session.phase_title}</span>
            <StatusBadge status={session.status} />
          </div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-900">
            {session.title}
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed whitespace-pre-line text-zinc-600">
            {session.description}
          </p>
        </div>
        {session.next_session_id ? (
          <Button
            asChild
            variant="outline"
            className="shrink-0 self-start"
            title={session.next_session_title ?? undefined}
          >
            <Link to={`/sessions/${session.next_session_id}`}>
              Next material
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
          </Button>
        ) : null}
      </header>

      <div className="grid gap-5 lg:grid-cols-[1fr_300px]">
        <aside className="space-y-4 lg:order-2">
          <Card>
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Actions</p>
            <div className="mt-3 space-y-2">
              {!isCompleted && !isInProgress ? (
                <Button
                  className="w-full"
                  onClick={() => actions.start.mutate()}
                  disabled={actions.start.isPending}
                >
                  <Play className="h-4 w-4" aria-hidden />
                  {actions.start.isPending ? "Starting…" : "Start Session"}
                </Button>
              ) : null}

              {!isCompleted ? (
                <Button
                  variant={isInProgress ? "default" : "outline"}
                  className="w-full"
                  onClick={() => setDialogOpen(true)}
                >
                  <CheckCircle2 className="h-4 w-4" aria-hidden />
                  Mark as Completed
                </Button>
              ) : null}

              {session.status !== "not_started" ? (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="danger"
                      className="w-full"
                      disabled={actions.reset.isPending}
                    >
                      <RotateCcw className="h-4 w-4" aria-hidden />
                      Reset Status
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Reset session status?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Start time, completion time, and actual duration will be cleared. Your
                        learning notes stay.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => actions.reset.mutate()}>
                        Reset session
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              ) : null}

              {!isCompleted && session.status !== "skipped" ? (
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => actions.skip.mutate()}
                  disabled={actions.skip.isPending}
                >
                  <SkipForward className="h-4 w-4" aria-hidden />
                  Skip Session
                </Button>
              ) : null}
            </div>
            {actionError ? <p className="mt-3 text-xs text-destructive">{actionError}</p> : null}
          </Card>

          <Card>
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Details</p>
            <dl className="mt-3 space-y-2.5 text-sm">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-zinc-500">Estimated</dt>
                <dd className="flex items-center gap-1 text-zinc-800">
                  <Clock className="h-3.5 w-3.5 text-zinc-400" aria-hidden />
                  {formatMinutes(session.estimated_duration_minutes)}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-zinc-500">Started</dt>
                <dd className="text-zinc-800">{formatDateTime(session.started_at)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-zinc-500">Completed</dt>
                <dd className="text-zinc-800">{formatDateTime(session.completed_at)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-zinc-500">Actual</dt>
                <dd className="text-zinc-800">{formatMinutes(session.actual_duration_minutes)}</dd>
              </div>
            </dl>
          </Card>
        </aside>

        <div className="space-y-4 lg:order-1">
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Link2 className="h-4 w-4 text-zinc-400" aria-hidden />
                <h2 className="text-sm font-semibold text-zinc-900">Learning material</h2>
              </div>
              {session.source_url ? (
                <Button asChild variant="outline" size="sm">
                  <a
                    href={withTimestamp(session.source_url, session.video_timestamp_seconds)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <ExternalLink className="h-3.5 w-3.5" aria-hidden />
                    {savedTimestamp ? `Open at ${savedTimestamp}` : "Open material"}
                  </a>
                </Button>
              ) : null}
            </div>
            <form
              className="mt-3"
              noValidate
              onSubmit={(event) => {
                event.preventDefault();
                actions.saveSource.mutate(sourceUrl.trim(), {
                  onSuccess: (data) => setSourceUrl(data.source_url),
                });
              }}
            >
              <Label htmlFor="session-source">Source link</Label>
              <div className="mt-1.5 flex gap-2">
                <Input
                  id="session-source"
                  type="url"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={sourceUrl}
                  onChange={(event) => setSourceUrl(event.target.value)}
                />
                <Button
                  type="submit"
                  variant="outline"
                  disabled={actions.saveSource.isPending || !sourceDirty}
                >
                  <Save className="h-4 w-4" aria-hidden />
                  {actions.saveSource.isPending ? "Saving…" : "Save"}
                </Button>
              </div>
              <p className="mt-1.5 text-xs text-muted-foreground">
                YouTube, documentation, or any learning source for this topic.
              </p>
              {actions.saveSource.error ? (
                <p className="mt-1.5 text-xs text-destructive">
                  {actions.saveSource.error.message}
                </p>
              ) : null}
              {actions.saveSource.isSuccess && !sourceDirty ? (
                <p className="mt-1.5 text-xs text-emerald-600">Link saved.</p>
              ) : null}
            </form>

            <form
              className="mt-4 space-y-1.5 border-t border-border pt-4"
              noValidate
              onSubmit={(event) => {
                event.preventDefault();
                const parsed = parseTimestamp(timestampInput);
                if (!parsed.ok) {
                  setTimestampError(parsed.error);
                  return;
                }
                setTimestampError(null);
                actions.saveTimestamp.mutate(parsed.seconds, {
                  onSuccess: (data) =>
                    setTimestampInput(formatTimestamp(data.video_timestamp_seconds)),
                });
              }}
            >
              <Label htmlFor="session-timestamp">Last watched timestamp</Label>
              <div className="flex gap-2">
                <Input
                  id="session-timestamp"
                  placeholder="12:34 or 1:02:03"
                  value={timestampInput}
                  onChange={(event) => setTimestampInput(event.target.value)}
                />
                <Button
                  type="submit"
                  variant="outline"
                  disabled={actions.saveTimestamp.isPending || !timestampDirty}
                >
                  <Clock className="h-4 w-4" aria-hidden />
                  {actions.saveTimestamp.isPending ? "Saving…" : "Save time"}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                {savedTimestamp
                  ? `Saved at ${savedTimestamp} — Open material resumes there (YouTube only).`
                  : "Optional. Accepts mm:ss, hh:mm:ss, or total seconds; Open material resumes there (YouTube only)."}
              </p>
              {timestampError ? (
                <p className="text-xs text-destructive">{timestampError}</p>
              ) : null}
              {actions.saveTimestamp.error ? (
                <p className="text-xs text-destructive">
                  {actions.saveTimestamp.error.message}
                </p>
              ) : null}
              {actions.saveTimestamp.isSuccess && !timestampDirty ? (
                <p className="text-xs text-emerald-600">Timestamp saved.</p>
              ) : null}
            </form>
          </Card>

          <Card>
            <div className="flex items-center gap-2">
              <ListChecks className="h-4 w-4 text-zinc-400" aria-hidden />
              <h2 className="text-sm font-semibold text-zinc-900">Learning objectives</h2>
            </div>
            <ul className="mt-3 space-y-2">
              {session.learning_objectives.map((objective) => (
                <li key={objective} className="flex gap-2 text-sm text-zinc-700">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-zinc-300" />
                  {objective}
                </li>
              ))}
            </ul>

            {session.topics.length > 0 ? (
              <>
                <h3 className="mt-4 text-xs font-medium uppercase tracking-wide text-zinc-500">
                  Topics
                </h3>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {session.topics.map((topic) => (
                    <span
                      key={topic}
                      className="rounded-md border border-zinc-200 bg-zinc-50 px-2 py-0.5 text-xs text-zinc-600"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </>
            ) : null}

            <h3 className="mt-4 text-xs font-medium uppercase tracking-wide text-zinc-500">
              Expected deliverable
            </h3>
            <p className="mt-1 text-sm text-zinc-700">{session.expected_deliverable}</p>
          </Card>

          <Card>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-sm font-semibold text-zinc-900">Learning notes</h2>
                <p className="mt-0.5 text-xs text-zinc-500">
                  Write freely. Notes are saved independently from the session status.
                </p>
              </div>
              <span className="text-xs text-zinc-400">
                {notesDirty ? "Unsaved changes" : "All changes saved"}
              </span>
            </div>

            <div className="mt-4 space-y-4">
              <NotesField
                label="What I Learned"
                value={notes.what_i_learned}
                onChange={update("what_i_learned")}
                placeholder="Key ideas from this session…"
              />
              <NotesField
                label="What I Understand"
                value={notes.what_i_understand}
                onChange={update("what_i_understand")}
                placeholder="Concepts that now make sense…"
              />
              <NotesField
                label="What I Don't Understand Yet"
                value={notes.what_i_dont_understand}
                onChange={update("what_i_dont_understand")}
                placeholder="Open questions, confusing parts…"
              />
              <NotesField
                label="Implementation Notes"
                value={notes.implementation_notes}
                onChange={update("implementation_notes")}
                placeholder="What did you build or try?"
              />
            </div>

            <div className="mt-4 flex items-center gap-3">
              <Button
                onClick={() => actions.saveNotes.mutate(notesPayload(notes))}
                disabled={actions.saveNotes.isPending || !notesDirty}
              >
                <Save className="h-4 w-4" aria-hidden />
                {actions.saveNotes.isPending ? "Saving…" : "Save Notes"}
              </Button>
              {actions.saveNotes.isSuccess && !notesDirty ? (
                <span className="text-xs text-emerald-600">Notes saved.</span>
              ) : null}
            </div>
          </Card>
        </div>
      </div>

      {dialogOpen ? (
        <CompleteDialog
          session={session}
          pending={actions.complete.isPending}
          error={actions.complete.error?.message ?? null}
          onCancel={() => setDialogOpen(false)}
          onConfirm={(minutes) => {
            actions.complete.mutate(
              { actual_duration_minutes: minutes, ...notesPayload(notes) },
              { onSuccess: () => setDialogOpen(false) },
            );
          }}
        />
      ) : null}
    </div>
  );
}

export function SessionPage() {
  const { sessionId } = useParams();
  const id = Number(sessionId);
  const { data, isPending, isError, error } = useSession(id);

  if (!sessionId || !Number.isFinite(id)) {
    return <ErrorState message="Invalid session id." />;
  }
  if (isPending) return <LoadingState label="Loading session…" />;
  if (isError) return <ErrorState message={error.message} />;

  return <SessionView key={data.id} session={data} />;
}
