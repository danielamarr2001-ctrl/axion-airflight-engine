const SEGMENT_STATUS_MAP: Record<string, string> = {
  HK: "SCHEDULED",
  XX: "CANCELLED",
  TK: "SCHEDULE CHANGE",
  UN: "UNABLE",
  UC: "UNABLE - CLOSED",
  NO: "NO ACTION",
};

export function translateSegmentStatus(gdsCode: string): string {
  return SEGMENT_STATUS_MAP[gdsCode.toUpperCase()] || gdsCode;
}

export function segmentStatusVariant(gdsCode: string): "scheduled" | "cancelled" | "escalated" | "secondary" {
  switch (gdsCode.toUpperCase()) {
    case "HK": return "scheduled";
    case "XX": return "cancelled";
    case "TK": return "escalated";
    default: return "secondary";
  }
}

export function decisionStatusVariant(status: string): "approved" | "rejected" | "escalated" | "confirmed" | "secondary" {
  switch (status.toUpperCase()) {
    case "APPROVED": return "approved";
    case "REJECTED": return "rejected";
    case "ESCALATED": return "escalated";
    case "CONFIRMED": return "confirmed";
    default: return "secondary";
  }
}

export function seatAvailabilityLevel(seats: number): "high" | "medium" | "low" {
  if (seats > 20) return "high";
  if (seats >= 5) return "medium";
  return "low";
}
