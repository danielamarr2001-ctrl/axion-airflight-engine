import type { ProcessorState, ProcessorAction } from "@/lib/types";

export const initialState: ProcessorState = { step: "IDLE" };

export function processorReducer(state: ProcessorState, action: ProcessorAction): ProcessorState {
  switch (action.type) {
    case "LOOKUP_START":
      return { step: "LOOKUP_LOADING", pnr: action.pnr, lastName: action.lastName };

    case "LOOKUP_SUCCESS":
      if (state.step !== "LOOKUP_LOADING") return state;
      return { step: "RESERVATION_LOADED", reservation: action.reservation };

    case "LOOKUP_ERROR":
      if (state.step !== "LOOKUP_LOADING") return state;
      return { step: "LOOKUP_ERROR", error: action.error, pnr: state.pnr, lastName: state.lastName };

    case "EVALUATE_START":
      if (state.step !== "RESERVATION_LOADED") return state;
      return { step: "EVALUATING", reservation: state.reservation };

    case "EVALUATE_SUCCESS":
      if (state.step !== "EVALUATING") return state;
      {
        const decisionStep =
          action.decision.status === "APPROVED" ? ("DECISION_APPROVED" as const) :
          action.decision.status === "ESCALATED" ? ("DECISION_ESCALATED" as const) :
          ("DECISION_REJECTED" as const);
        return { step: decisionStep, reservation: state.reservation, decision: action.decision };
      }

    case "EVALUATE_ERROR":
      if (state.step !== "EVALUATING") return state;
      return { step: "EVALUATION_ERROR", reservation: state.reservation, error: action.error };

    case "SELECT_OPTION":
      if (state.step !== "DECISION_APPROVED") return state;
      return { step: "CONFIRMING", reservation: state.reservation, decision: state.decision, selectedOptionId: action.optionId };

    case "CANCEL_SELECTION":
      if (state.step !== "CONFIRMING" && state.step !== "SELECTION_ERROR") return state;
      return { step: "DECISION_APPROVED", reservation: state.reservation, decision: state.decision };

    case "CONFIRM_START":
      if (state.step !== "CONFIRMING") return state;
      return { step: "SELECTION_LOADING", reservation: state.reservation, decision: state.decision, selectedOptionId: state.selectedOptionId };

    case "CONFIRM_SUCCESS":
      if (state.step !== "SELECTION_LOADING") return state;
      return { step: "DECISION_RECORDED", reservation: state.reservation, decision: state.decision, confirmation: action.confirmation };

    case "CONFIRM_ERROR":
      if (state.step !== "SELECTION_LOADING") return state;
      return { step: "SELECTION_ERROR", reservation: state.reservation, decision: state.decision, selectedOptionId: state.selectedOptionId, error: action.error };

    case "RESET":
      return { step: "IDLE" };

    default:
      return state;
  }
}
