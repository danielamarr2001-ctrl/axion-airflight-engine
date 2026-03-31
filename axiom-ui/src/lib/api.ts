import type { Reservation, EvaluateResponse, SelectResponse, MetricsResponse } from "./types";

const API_BASE = "/api";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export function lookupReservation(pnr: string, lastName: string) {
  return apiFetch<Reservation>("/lookup", {
    method: "POST",
    body: JSON.stringify({ pnr, last_name: lastName }),
  });
}

export function evaluateReservation(pnr: string, reservationId: number) {
  return apiFetch<EvaluateResponse>("/evaluate", {
    method: "POST",
    body: JSON.stringify({ pnr, reservation_id: reservationId }),
  });
}

export function selectOption(decisionId: number, selectedOption: string, operatorNotes: string) {
  return apiFetch<SelectResponse>("/select", {
    method: "POST",
    body: JSON.stringify({
      decision_id: decisionId,
      selected_option: selectedOption,
      operator_notes: operatorNotes,
    }),
  });
}

export function fetchMetrics() {
  return apiFetch<MetricsResponse>("/metrics");
}
