import type { FlightOption } from "@/lib/types";
import { seatAvailabilityLevel } from "@/lib/translations";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function formatDate(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function seatBadgeClasses(level: "high" | "medium" | "low"): string {
  switch (level) {
    case "high":
      return "bg-[oklch(0.7_0.15_145/0.15)] text-[var(--color-chart-3)]";
    case "medium":
      return "bg-[oklch(0.7_0.15_55/0.15)] text-[var(--color-chart-4)]";
    case "low":
      return "bg-[oklch(0.55_0.2_25/0.15)] text-destructive";
  }
}

interface FlightOptionCardProps {
  option: FlightOption;
  selected: boolean;
  onSelect: (optionId: number) => void;
  disabled?: boolean;
}

export function FlightOptionCard({ option, selected, onSelect, disabled }: FlightOptionCardProps) {
  const level = seatAvailabilityLevel(option.available_seats);

  return (
    <Card
      className={`p-4 transition-colors duration-150 hover:border-primary/50 ${
        selected ? "ring-2 ring-primary" : ""
      }`}
    >
      <div className="space-y-3">
        {/* Flight number */}
        <p className="text-base font-semibold font-mono">
          {option.flight_number}
        </p>

        {/* Route */}
        <p className="text-sm font-mono text-muted-foreground">
          {option.origin} &rarr; {option.destination}
        </p>

        {/* Date */}
        <p className="text-sm text-muted-foreground">
          {formatDate(option.departure_date)}
        </p>

        {/* Time window */}
        <p className="text-sm font-mono">
          {option.departure_time} - {option.arrival_time}
        </p>

        {/* Aircraft */}
        {option.aircraft_type && (
          <p className="text-xs text-muted-foreground">
            {option.aircraft_type}
          </p>
        )}

        {/* Availability */}
        <div>
          <span
            className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${seatBadgeClasses(level)}`}
          >
            {option.available_seats} seats available
          </span>
        </div>

        {/* Fare class */}
        <p className="text-sm">Class {option.fare_class}</p>

        {/* Select button */}
        <Button
          className="w-full min-h-[36px]"
          disabled={disabled}
          onClick={() => onSelect(option.id)}
        >
          Select Flight
        </Button>
      </div>
    </Card>
  );
}
