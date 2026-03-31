import type { EvaluateResponse } from "@/lib/types";
import { decisionStatusVariant } from "@/lib/translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, AlertTriangle } from "lucide-react";

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "APPROVED":
      return <CheckCircle2 className="h-6 w-6 mr-2 inline" />;
    case "REJECTED":
      return <XCircle className="h-6 w-6 mr-2 inline" />;
    case "ESCALATED":
      return <AlertTriangle className="h-6 w-6 mr-2 inline" />;
    default:
      return null;
  }
}

function statusDisplayText(status: string): string {
  switch (status) {
    case "APPROVED":
      return "Reprotection Approved";
    case "REJECTED":
      return "Reprotection Rejected";
    case "ESCALATED":
      return "Manual Review Required";
    default:
      return status;
  }
}

interface DecisionPanelProps {
  decision: EvaluateResponse;
}

export function DecisionPanel({ decision }: DecisionPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl">Decision</CardTitle>
      </CardHeader>
      <Separator />
      <CardContent className="pt-6">
        {/* Centered oversized status badge */}
        <div className="flex flex-col items-center py-6 space-y-4 animate-in fade-in duration-200">
          <Badge
            variant={decisionStatusVariant(decision.status)}
            className="text-2xl font-semibold px-6 py-3"
          >
            <StatusIcon status={decision.status} />
            {statusDisplayText(decision.status)}
          </Badge>

          {/* Rule applied */}
          <p className="text-sm text-muted-foreground">
            Rule Applied: {decision.rule_applied}
          </p>
        </div>

        {/* Justification */}
        <div className="bg-muted/50 rounded-md p-3 mt-4">
          <p className="text-xs text-muted-foreground font-semibold mb-1">
            Justification:
          </p>
          <p className="text-sm">{decision.justification}</p>
        </div>

        {/* Terminal messages for REJECTED / ESCALATED */}
        {decision.status === "REJECTED" && (
          <div className="mt-4 p-3 rounded-md bg-muted/30">
            <p className="text-sm text-muted-foreground">
              No reprotection options available. This reservation does not qualify for automated reprotection.
            </p>
          </div>
        )}
        {decision.status === "ESCALATED" && (
          <div className="mt-4 p-3 rounded-md bg-muted/30">
            <p className="text-sm text-muted-foreground">
              This case requires manual review. Escalate to a senior agent for further assessment.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
