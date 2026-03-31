import type { FlightOption } from "@/lib/types";
import { FlightOptionCard } from "./flight-option-card";

interface ReprotectionOptionsProps {
  options: FlightOption[];
  selectedOptionId: number | null;
  onSelect: (optionId: number) => void;
  disabled?: boolean;
}

function gridColsClass(count: number): string {
  if (count === 3) return "grid-cols-1 sm:grid-cols-3";
  if (count <= 2) return "grid-cols-1 sm:grid-cols-2";
  return "grid-cols-1 sm:grid-cols-2 xl:grid-cols-4";
}

export function ReprotectionOptions({
  options,
  selectedOptionId,
  onSelect,
  disabled,
}: ReprotectionOptionsProps) {
  return (
    <div
      className="animate-in fade-in slide-in-from-bottom-2 duration-200"
      style={{ animationDelay: "100ms", animationFillMode: "backwards" }}
    >
      <h2 className="text-xl font-semibold">Reprotection Options</h2>
      <p className="text-sm text-muted-foreground mb-4">
        Select an alternative flight for the affected passengers.
      </p>

      <div className={`grid ${gridColsClass(options.length)} gap-4`}>
        {options.map((opt) => (
          <FlightOptionCard
            key={opt.id}
            option={opt}
            selected={opt.id === selectedOptionId}
            onSelect={onSelect}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  );
}
