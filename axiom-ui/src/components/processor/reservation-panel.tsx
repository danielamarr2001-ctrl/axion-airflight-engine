import type { Reservation } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { PassengersTable } from "./passengers-table";
import { SegmentsTable } from "./segments-table";

interface ReservationPanelProps {
  reservation: Reservation;
}

export function ReservationPanel({ reservation }: ReservationPanelProps) {
  const hasCancelledSegment = reservation.segments.some((s) => s.status === "XX");

  return (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-150">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl">
              Reservation <span className="font-mono">{reservation.pnr}</span>
            </CardTitle>
            {hasCancelledSegment ? (
              <Badge variant="cancelled">DISRUPTED</Badge>
            ) : (
              <Badge variant="scheduled">ACTIVE</Badge>
            )}
          </div>
        </CardHeader>
        <Separator />
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">
                Passengers
              </h3>
              <PassengersTable passengers={reservation.passengers} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">
                Segments
              </h3>
              <SegmentsTable segments={reservation.segments} />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
