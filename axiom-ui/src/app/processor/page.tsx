"use client";

import { useReducer, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { lookupReservation, evaluateReservation } from "@/lib/api";
import { processorReducer } from "./reducer";
import type { ProcessorState } from "@/lib/types";
import { PnrLookupForm } from "@/components/processor/pnr-lookup-form";
import { ReservationPanel } from "@/components/processor/reservation-panel";
import { ReservationSkeleton } from "@/components/processor/reservation-skeleton";
import { RuleTraceSkeleton } from "@/components/processor/rule-trace-skeleton";
import { DecisionSkeleton } from "@/components/processor/decision-skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

export default function ProcessorPage() {
  const [state, dispatch] = useReducer(processorReducer, { step: "IDLE" } as ProcessorState);

  // Ref to hold pnr/reservationId for evaluate chaining
  const lookupDataRef = useRef<{ pnr: string; reservationId: number } | null>(null);

  const evaluateMutation = useMutation({
    mutationFn: (data: { pnr: string; reservationId: number }) =>
      evaluateReservation(data.pnr, data.reservationId),
    onSuccess: (decision) => {
      dispatch({ type: "EVALUATE_SUCCESS", decision });
    },
    onError: (error: Error) => {
      dispatch({ type: "EVALUATE_ERROR", error: error.message });
    },
  });

  const lookupMutation = useMutation({
    mutationFn: (data: { pnr: string; lastName: string }) =>
      lookupReservation(data.pnr, data.lastName),
    onMutate: (data) => {
      dispatch({ type: "LOOKUP_START", pnr: data.pnr, lastName: data.lastName });
    },
    onSuccess: (reservation) => {
      dispatch({ type: "LOOKUP_SUCCESS", reservation });
      dispatch({ type: "EVALUATE_START" });
      lookupDataRef.current = { pnr: reservation.pnr, reservationId: reservation.id };
      evaluateMutation.mutate({ pnr: reservation.pnr, reservationId: reservation.id });
    },
    onError: (error: Error) => {
      dispatch({ type: "LOOKUP_ERROR", error: error.message });
    },
  });

  // Derive visibility flags from state
  const isFormDisabled = state.step === "LOOKUP_LOADING" || state.step === "SELECTION_LOADING";
  const showReservationSkeleton = state.step === "LOOKUP_LOADING";
  const showReservation = "reservation" in state;
  const showLookupError = state.step === "LOOKUP_ERROR";
  const showEvaluationError = state.step === "EVALUATION_ERROR";
  const showRuleTraceSkeleton = state.step === "EVALUATING" || state.step === "RESERVATION_LOADED";
  const showDecisionSkeleton = state.step === "EVALUATING";

  return (
    <div className="space-y-6">
      {/* Page header -- 24px semibold per UI-SPEC */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Processor</h1>
        <p className="text-sm text-muted-foreground">
          Look up a PNR and process involuntary change decisions.
        </p>
      </div>

      {/* PNR Form -- always visible */}
      <PnrLookupForm
        onSubmit={(pnr, lastName) => lookupMutation.mutate({ pnr, lastName })}
        disabled={isFormDisabled}
        loading={state.step === "LOOKUP_LOADING"}
      />

      {/* Lookup Error */}
      {showLookupError && state.step === "LOOKUP_ERROR" && (
        <Alert variant="destructive" className="animate-in fade-in duration-150">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>PNR not found</AlertTitle>
          <AlertDescription>
            No reservation matches PNR &quot;{state.pnr}&quot; with last name &quot;{state.lastName}&quot;.
            Verify the PNR code and passenger last name, then try again.
          </AlertDescription>
        </Alert>
      )}

      {/* Evaluation Error */}
      {showEvaluationError && (
        <Alert variant="destructive" className="animate-in fade-in duration-150">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Evaluation failed</AlertTitle>
          <AlertDescription>
            Rule evaluation failed. The decision engine could not process this reservation. Please try the lookup again.
          </AlertDescription>
        </Alert>
      )}

      {/* Reservation Skeleton */}
      {showReservationSkeleton && <ReservationSkeleton />}

      {/* Reservation Panel */}
      {showReservation && "reservation" in state && (
        <ReservationPanel reservation={state.reservation} />
      )}

      {/* Rule Trace + Decision skeletons during evaluation */}
      {(showRuleTraceSkeleton || showDecisionSkeleton) && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {showRuleTraceSkeleton && <RuleTraceSkeleton />}
          {showDecisionSkeleton && <DecisionSkeleton />}
        </div>
      )}

      {/* Decision components placeholder -- wired in Plan 02 */}
    </div>
  );
}
