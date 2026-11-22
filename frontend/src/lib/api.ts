import type {
  CompletePayload,
  Dashboard,
  HistoryFilters,
  HistoryItem,
  NotesPayload,
  Phase,
  ProgressOverview,
  SessionDetail,
} from "../types";

// Relative by default: the Vite dev server proxies /api to the backend.
// Set VITE_API_URL when serving the built frontend against another origin.
const API_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
  } catch {
    throw new ApiError("Cannot reach the API. Is the backend running?", 0);
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
      else if (Array.isArray(body.detail)) {
        const first = body.detail[0] as { msg?: unknown } | undefined;
        detail =
          typeof first?.msg === "string"
            ? first.msg.replace(/^Value error, /, "")
            : "Please check the values you submitted.";
      }
    } catch {
      // Non-JSON error body; keep the generic message.
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}

function historyQuery(filters: HistoryFilters): string {
  const params = new URLSearchParams();
  if (filters.week) params.set("week", String(filters.week));
  if (filters.status) params.set("status", filters.status);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const api = {
  dashboard: () => request<Dashboard>("/dashboard"),
  phases: () => request<Phase[]>("/phases"),
  phase: (id: number) => request<Phase>(`/phases/${id}`),
  session: (id: number) => request<SessionDetail>(`/sessions/${id}`),
  history: (filters: HistoryFilters) =>
    request<HistoryItem[]>(`/history${historyQuery(filters)}`),
  progress: () => request<ProgressOverview>("/progress"),
  startSession: (id: number) =>
    request<SessionDetail>(`/sessions/${id}/start`, { method: "POST" }),
  completeSession: (id: number, payload: CompletePayload) =>
    request<SessionDetail>(`/sessions/${id}/complete`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  saveNotes: (id: number, payload: NotesPayload) =>
    request<SessionDetail>(`/sessions/${id}/notes`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  saveSource: (id: number, sourceUrl: string) =>
    request<SessionDetail>(`/sessions/${id}/source`, {
      method: "PATCH",
      body: JSON.stringify({ source_url: sourceUrl }),
    }),
  saveTimestamp: (id: number, seconds: number | null) =>
    request<SessionDetail>(`/sessions/${id}/timestamp`, {
      method: "PATCH",
      body: JSON.stringify({ seconds }),
    }),
  resetSession: (id: number) =>
    request<SessionDetail>(`/sessions/${id}/reset`, { method: "POST" }),
  skipSession: (id: number) =>
    request<SessionDetail>(`/sessions/${id}/skip`, { method: "POST" }),
};
