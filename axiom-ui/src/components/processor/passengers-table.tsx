import type { Passenger } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface PassengersTableProps {
  passengers: Passenger[];
}

export function PassengersTable({ passengers }: PassengersTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="text-xs py-2 px-2">Passenger</TableHead>
          <TableHead className="text-xs py-2 px-2 w-40">Ticket</TableHead>
          <TableHead className="text-xs py-2 px-2 w-20">Fare Class</TableHead>
          <TableHead className="text-xs py-2 px-2 w-15">Type</TableHead>
          <TableHead className="text-xs py-2 px-2 w-15">SSR</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {passengers.map((p) => (
          <TableRow key={p.id}>
            <TableCell className="py-2 px-2 font-mono">
              {p.last_name}/{p.first_name}
            </TableCell>
            <TableCell className="py-2 px-2 font-mono w-40">
              {p.ticket_number || "---"}
            </TableCell>
            <TableCell className="py-2 px-2 w-20">
              <Badge variant="secondary" className="font-mono">
                {p.fare_class}
              </Badge>
            </TableCell>
            <TableCell className="py-2 px-2 w-15">
              {p.passenger_type}
            </TableCell>
            <TableCell className="py-2 px-2 w-15">
              {p.ssr_records.length > 0 ? (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge variant="secondary" className="cursor-help">
                        {p.ssr_records.length}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{p.ssr_records.map((s) => s.ssr_type).join(", ")}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              ) : (
                <span className="text-muted-foreground">---</span>
              )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
