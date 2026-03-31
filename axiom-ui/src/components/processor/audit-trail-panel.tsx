import type { Reservation, EvaluateResponse, SelectResponse } from "@/lib/types";
import { translateSegmentStatus } from "@/lib/translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

function formatTimestamp(iso: string): string {
  try {
    const date = new Date(iso);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return iso;
  }
}

interface TimelineEntry {
  timestamp: string;
  title: string;
  details: string[];
  badge?: { text: string; variant: "confirmed" | "approved" | "cancelled" | "secondary" };
}

interface AuditTrailPanelProps {
  reservation: Reservation;
  decision: EvaluateResponse;
  confirmation: SelectResponse;
}

export function AuditTrailPanel({ reservation, decision, confirmation }: AuditTrailPanelProps) {
  const passedCount = decision.trace.filter((t) => t.result === "PASS").length;
  const cancelledCount = reservation.segments.filter(
    (s) => translateSegmentStatus(s.status) === "CANCELLED"
  ).length;

  const entries: TimelineEntry[] = [
    {
      timestamp: formatTimestamp(confirmation.timestamp),
      title: "Decision recorded",
      details: [
        `Selected: ${confirmation.selected_option}`,
      ],
      badge: { text: "CONFIRMED", variant: "confirmed" },
    },
    {
      timestamp: "Moments ago",
      title: "Reprotection approved",
      details: [
        `Rule: ${decision.rule_applied}`,
        `${passedCount}/${decision.trace.length} checks passed`,
      ],
    },
    {
      timestamp: formatTimestamp(reservation.created_at),
      title: `PNR ${reservation.pnr} retrieved`,
      details: [
        `${reservation.passengers.length} passengers, ${reservation.segments.length} segments`,
        `${cancelledCount} segment CANCELLED`,
      ],
    },
  ];

  return (
    <Card className="animate-in fade-in slide-in-from-bottom-2 duration-200">
      <CardHeader>
        <CardTitle className="text-xl">Audit Trail</CardTitle>
      </CardHeader>
      <Separator />
      <CardContent className="pt-6">
        <div>
          {entries.map((entry, i) => (
            <div
              key={i}
              className={`relative pl-6 ${i < entries.length - 1 ? "pb-6" : "pb-0"}`}
            >
              {/* Timeline marker */}
              <div className="absolute left-0 top-1.5 h-2 w-2 rounded-full bg-primary" />
              {/* Vertical connector */}
              {i < entries.length - 1 && (
                <div className="absolute left-[3px] top-3 bottom-0 w-0.5 bg-border" />
              )}

              {/* Timestamp */}
              <p className="font-mono text-xs text-muted-foreground">
                {entry.timestamp}
              </p>

              {/* Title */}
              <p className="text-sm font-semibold mt-0.5">
                {entry.title}
                {entry.badge && (
                  <Badge variant={entry.badge.variant} className="ml-2">
                    {entry.badge.text}
                  </Badge>
                )}
              </p>

              {/* Details */}
              <div className="ml-0 mt-1 space-y-0.5">
                {entry.details.map((detail, j) => (
                  <p key={j} className="text-xs text-muted-foreground">
                    {detail}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
