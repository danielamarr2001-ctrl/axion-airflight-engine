export interface SSRRecord {
  id: number;
  ssr_type: string;
  ssr_detail: string | null;
}

export interface Passenger {
  id: number;
  last_name: string;
  first_name: string;
  ticket_number: string | null;
  fare_class: string;
  fare_basis: string | null;
  passenger_type: string;
  ssr_records: SSRRecord[];
}

export interface Segment {
  id: number;
  flight_number: string;
  airline: string;
  origin: string;
  destination: string;
  departure_date: string;
  departure_time: string;
  arrival_time: string;
  status: string;
  cabin_class: string;
  aircraft_type: string | null;
}

export interface Reservation {
  id: number;
  pnr: string;
  booking_reference: string | null;
  created_at: string;
  passengers: Passenger[];
  segments: Segment[];
}

export interface RuleTraceItem {
  step: string;
  result: string;
  detail: string;
}

export interface FlightOption {
  id: number;
  flight_number: string;
  airline: string;
  origin: string;
  destination: string;
  departure_date: string;
  departure_time: string;
  arrival_time: string;
  available_seats: number;
  fare_class: string;
  aircraft_type: string | null;
  status: string;
}

export interface EvaluateResponse {
  decision_id: number;
  status: "APPROVED" | "REJECTED" | "ESCALATED";
  rule_applied: string;
  justification: string;
  trace: RuleTraceItem[];
  options: FlightOption[];
}

export interface SelectResponse {
  id: number;
  status: string;
  selected_option: string;
  pnr: string;
  timestamp: string;
}

export type ProcessorState =
  | { step: "IDLE" }
  | { step: "LOOKUP_LOADING"; pnr: string; lastName: string }
  | { step: "LOOKUP_ERROR"; error: string; pnr: string; lastName: string }
  | { step: "RESERVATION_LOADED"; reservation: Reservation }
  | { step: "EVALUATING"; reservation: Reservation }
  | { step: "EVALUATION_ERROR"; reservation: Reservation; error: string }
  | { step: "DECISION_APPROVED"; reservation: Reservation; decision: EvaluateResponse }
  | { step: "DECISION_REJECTED"; reservation: Reservation; decision: EvaluateResponse }
  | { step: "DECISION_ESCALATED"; reservation: Reservation; decision: EvaluateResponse }
  | { step: "CONFIRMING"; reservation: Reservation; decision: EvaluateResponse; selectedOptionId: number }
  | { step: "SELECTION_LOADING"; reservation: Reservation; decision: EvaluateResponse; selectedOptionId: number }
  | { step: "SELECTION_ERROR"; reservation: Reservation; decision: EvaluateResponse; selectedOptionId: number; error: string }
  | { step: "DECISION_RECORDED"; reservation: Reservation; decision: EvaluateResponse; confirmation: SelectResponse };

export type ProcessorAction =
  | { type: "LOOKUP_START"; pnr: string; lastName: string }
  | { type: "LOOKUP_SUCCESS"; reservation: Reservation }
  | { type: "LOOKUP_ERROR"; error: string }
  | { type: "EVALUATE_START" }
  | { type: "EVALUATE_SUCCESS"; decision: EvaluateResponse }
  | { type: "EVALUATE_ERROR"; error: string }
  | { type: "SELECT_OPTION"; optionId: number }
  | { type: "CANCEL_SELECTION" }
  | { type: "CONFIRM_START" }
  | { type: "CONFIRM_SUCCESS"; confirmation: SelectResponse }
  | { type: "CONFIRM_ERROR"; error: string }
  | { type: "RESET" };

export interface DailyDecisions {
  date: string; // ISO date "2026-04-01"
  count: number;
  approved: number;
  escalated: number;
  rejected: number;
}

export interface RuleCount {
  rule: string; // e.g. "involuntary_change"
  count: number;
}

export interface MetricsResponse {
  total_decisions: number;
  automation_rate: number; // 0-100 percentage
  avg_processing_time_ms: number;
  decisions_by_day: DailyDecisions[];
  top_rules: RuleCount[];
  decisions_by_status: {
    APPROVED: number;
    REJECTED: number;
    ESCALATED: number;
  };
}
