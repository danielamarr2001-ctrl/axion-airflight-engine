import type { RuleTraceItem } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

function formatStepLabel(step: string): string {
  return step
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function resultToVariant(result: string): "approved" | "rejected" | "escalated" | "secondary" {
  switch (result.toUpperCase()) {
    case "PASS":
      return "approved";
    case "FAIL":
      return "rejected";
    case "WARN":
      return "escalated";
    default:
      return "secondary";
  }
}

function resultToIndicatorClass(result: string): string {
  switch (result.toUpperCase()) {
    case "PASS":
      return "bg-primary";
    case "FAIL":
      return "bg-destructive";
    case "WARN":
      return "bg-[var(--color-chart-4)]";
    default:
      return "bg-muted-foreground";
  }
}

interface RuleTracePanelProps {
  trace: RuleTraceItem[];
}

export function RuleTracePanel({ trace }: RuleTracePanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl">Rule Evaluation</CardTitle>
      </CardHeader>
      <Separator />
      <CardContent className="pt-6">
        <div className="space-y-4">
          {trace.map((item, i) => (
            <div
              key={i}
              className="flex items-start gap-3 relative animate-in fade-in"
              style={{ animationDelay: `${i * 50}ms`, animationFillMode: "backwards" }}
            >
              {/* Circle indicator */}
              <div className="relative flex flex-col items-center">
                <div
                  className={`h-4 w-4 rounded-full shrink-0 ${resultToIndicatorClass(item.result)}`}
                />
                {/* Vertical connector line (not on last item) */}
                {i < trace.length - 1 && (
                  <div className="absolute left-[7px] top-4 bottom-0 w-0.5 border-l-2 border-dashed border-border" />
                )}
              </div>

              {/* Step content */}
              <div className="flex-1 min-w-0 pb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{formatStepLabel(item.step)}</span>
                  <Badge variant={resultToVariant(item.result)}>
                    {item.result}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {item.detail}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
