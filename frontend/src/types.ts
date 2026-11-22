export type SessionStatus = "not_started" | "in_progress" | "completed" | "skipped";
export type PhaseStatus = "not_started" | "in_progress" | "completed";

export interface Session {
  id: number;
  phase_id: number;
  title: string;
  description: string;
  learning_objectives: string[];
  topics: string[];
  expected_deliverable: string;
  source_url: string;
  estimated_duration_minutes: number;
  order_index: number;
  status: SessionStatus;
  started_at: string | null;
  completed_at: string | null;
  actual_duration_minutes: number | null;
  video_timestamp_seconds: number | null;
  what_i_learned: string;
  what_i_understand: string;
  what_i_dont_understand: string;
  implementation_notes: string;
}

export interface SessionDetail extends Session {
  week_number: number;
  phase_title: string;
  next_session_id: number | null;
  next_session_title: string | null;
}

export interface Phase {
  id: number;
  week_number: number;
  title: string;
  description: string;
  order_index: number;
  status: PhaseStatus;
  progress_percent: number;
  completed_sessions: number;
  total_sessions: number;
  sessions: Session[];
}

export interface SessionBrief {
  id: number;
  title: string;
  week_number: number;
  session_number: number;
  status: SessionStatus;
  estimated_duration_minutes: number;
  learning_objectives: string[];
}

export interface OverallStats {
  completed_phases: number;
  total_phases: number;
  completed_sessions: number;
  total_sessions: number;
  progress_percent: number;
  total_learning_minutes: number;
  total_learning_hours: number;
}

export interface SessionCounts {
  completed: number;
  in_progress: number;
  not_started: number;
  skipped: number;
  total: number;
}

export interface CurrentPhase {
  id: number;
  week_number: number;
  title: string;
  status: PhaseStatus;
  progress_percent: number;
  completed_sessions: number;
  total_sessions: number;
  next_session: SessionBrief | null;
}

export interface RecentActivity {
  session_id: number;
  title: string;
  week_number: number;
  completed_at: string;
  actual_duration_minutes: number | null;
}

export interface Dashboard {
  overall: OverallStats;
  counts: SessionCounts;
  current_phase: CurrentPhase | null;
  next_session: SessionBrief | null;
  recent_activity: RecentActivity[];
  curriculum_completed: boolean;
}

export interface HistoryItem {
  session_id: number;
  title: string;
  week_number: number;
  phase_title: string;
  status: SessionStatus;
  activity_at: string | null;
  completed_at: string | null;
  actual_duration_minutes: number | null;
  note_excerpt: string;
}

export interface WeekProgress {
  week_number: number;
  title: string;
  status: PhaseStatus;
  completed_sessions: number;
  total_sessions: number;
  progress_percent: number;
  learning_minutes: number;
}

export interface ProgressOverview {
  progress_percent: number;
  completed_sessions: number;
  total_sessions: number;
  total_learning_minutes: number;
  total_learning_hours: number;
  weeks: WeekProgress[];
}

export interface HistoryFilters {
  week?: number;
  status?: SessionStatus;
  date_from?: string;
  date_to?: string;
}

export interface NotesPayload {
  what_i_learned?: string;
  what_i_understand?: string;
  what_i_dont_understand?: string;
  implementation_notes?: string;
}

export interface CompletePayload extends NotesPayload {
  actual_duration_minutes: number;
}
