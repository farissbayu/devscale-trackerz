import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { CompletePayload, HistoryFilters, NotesPayload } from "../types";

export const queryKeys = {
  dashboard: ["dashboard"] as const,
  phases: ["phases"] as const,
  phase: (id: number) => ["phase", id] as const,
  session: (id: number) => ["session", id] as const,
  history: (filters: HistoryFilters) => ["history", filters] as const,
  progress: ["progress"] as const,
};

export function useDashboard() {
  return useQuery({ queryKey: queryKeys.dashboard, queryFn: api.dashboard });
}

export function usePhases() {
  return useQuery({ queryKey: queryKeys.phases, queryFn: api.phases });
}

export function useSession(id: number) {
  return useQuery({
    queryKey: queryKeys.session(id),
    queryFn: () => api.session(id),
    enabled: Number.isFinite(id),
  });
}

export function useHistory(filters: HistoryFilters) {
  return useQuery({ queryKey: queryKeys.history(filters), queryFn: () => api.history(filters) });
}

export function useProgressOverview() {
  return useQuery({ queryKey: queryKeys.progress, queryFn: api.progress });
}

export function useSessionActions(sessionId: number) {
  const queryClient = useQueryClient();
  const refresh = () => queryClient.invalidateQueries();

  const start = useMutation({
    mutationFn: () => api.startSession(sessionId),
    onSuccess: refresh,
  });
  const complete = useMutation({
    mutationFn: (payload: CompletePayload) => api.completeSession(sessionId, payload),
    onSuccess: refresh,
  });
  const saveNotes = useMutation({
    mutationFn: (payload: NotesPayload) => api.saveNotes(sessionId, payload),
    onSuccess: refresh,
  });
  const saveSource = useMutation({
    mutationFn: (sourceUrl: string) => api.saveSource(sessionId, sourceUrl),
    onSuccess: refresh,
  });
  const saveTimestamp = useMutation({
    mutationFn: (seconds: number | null) => api.saveTimestamp(sessionId, seconds),
    onSuccess: refresh,
  });
  const reset = useMutation({
    mutationFn: () => api.resetSession(sessionId),
    onSuccess: refresh,
  });
  const skip = useMutation({
    mutationFn: () => api.skipSession(sessionId),
    onSuccess: refresh,
  });

  return { start, complete, saveNotes, saveSource, saveTimestamp, reset, skip };
}
