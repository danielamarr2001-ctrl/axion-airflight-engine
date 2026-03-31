import type { Segment } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { translateSegmentStatus, segmentStatusVariant } from "@/lib/translations";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

interface SegmentsTableProps {
  segments: Segment[];
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function SegmentsTable({ segments }: SegmentsTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="text-xs py-2 px-2 w-20">Flight</TableHead>
          <TableHead className="text-xs py-2 px-2 w-30">Route</TableHead>
          <TableHead className="text-xs py-2 px-2 w-25">Date</TableHead>
          <TableHead className="text-xs py-2 px-2 w-[70px]">Departure</TableHead>
          <TableHead className="text-xs py-2 px-2 w-[70px]">Arrival</TableHead>
          <TableHead className="text-xs py-2 px-2 w-25">Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {segments.map((s) => {
          const isCancelled = s.status === "XX";
          return (
            <TableRow
              key={s.id}
              className={cn(isCancelled && "bg-[oklch(0.55_0.2_25/0.05)]")}
            >
              <TableCell className="py-2 px-2 font-mono font-semibold w-20">
                {s.flight_number}
              </TableCell>
              <TableCell className="py-2 px-2 font-mono w-30">
                {s.origin} {"\u2192"} {s.destination}
              </TableCell>
              <TableCell className="py-2 px-2 w-25">
                {formatDate(s.departure_date)}
              </TableCell>
              <TableCell className="py-2 px-2 font-mono w-[70px]">
                {s.departure_time}
              </TableCell>
              <TableCell className="py-2 px-2 font-mono w-[70px]">
                {s.arrival_time}
              </TableCell>
              <TableCell className="py-2 px-2 w-25">
                <Badge variant={segmentStatusVariant(s.status)}>
                  {translateSegmentStatus(s.status)}
                </Badge>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
