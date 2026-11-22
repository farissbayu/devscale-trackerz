export type ParsedTimestamp =
  | { ok: true; seconds: number | null }
  | { ok: false; error: string };

/** Accepts total seconds ("754"), mm:ss ("12:34"), or hh:mm:ss ("1:02:03"). */
export function parseTimestamp(value: string): ParsedTimestamp {
  const input = value.trim();
  if (!input) return { ok: true, seconds: null };

  const parts = input.split(":").map((part) => part.trim());
  if (parts.length > 3 || parts.some((part) => !/^\d+$/.test(part))) {
    return { ok: false, error: "Use mm:ss, hh:mm:ss, or total seconds." };
  }

  const numbers = parts.map(Number);
  if (numbers.some((part) => part > 86400)) {
    return { ok: false, error: "Timestamp is too large." };
  }
  if (numbers.length > 1 && numbers[numbers.length - 1] >= 60) {
    return { ok: false, error: "Seconds must be below 60." };
  }
  if (numbers.length === 3 && numbers[1] >= 60) {
    return { ok: false, error: "Minutes must be below 60." };
  }

  let seconds: number;
  if (numbers.length === 1) seconds = numbers[0];
  else if (numbers.length === 2) seconds = numbers[0] * 60 + numbers[1];
  else seconds = numbers[0] * 3600 + numbers[1] * 60 + numbers[2];

  if (seconds > 86400) return { ok: false, error: "Timestamp is too large." };
  return { ok: true, seconds };
}

export function formatTimestamp(seconds: number | null | undefined): string {
  if (seconds == null) return "";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const rest = seconds % 60;
  const pad = (value: number) => String(value).padStart(2, "0");
  return hours > 0 ? `${hours}:${pad(minutes)}:${pad(rest)}` : `${minutes}:${pad(rest)}`;
}

/** Adds YouTube's `t=<seconds>s` param so the player resumes at the saved position. */
export function withTimestamp(url: string, seconds: number | null | undefined): string {
  if (!url || !seconds) return url;
  try {
    const parsed = new URL(url);
    if (/(^|\.)youtube\.com$|(^|\.)youtu\.be$/i.test(parsed.hostname)) {
      parsed.searchParams.set("t", `${seconds}s`);
    }
    return parsed.toString();
  } catch {
    return url;
  }
}
