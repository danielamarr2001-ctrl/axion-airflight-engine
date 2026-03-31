"use client";

import { useState } from "react";
import type { FlightOption, Segment } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Loader2 } from "lucide-react";

interface ConfirmationDialogProps {
  open: boolean;
  option: FlightOption | null;
  originalSegment: Segment | null;
  loading: boolean;
  error: string | null;
  onConfirm: (notes: string) => void;
  onCancel: () => void;
}

export function ConfirmationDialog({
  open,
  option,
  originalSegment,
  loading,
  error,
  onConfirm,
  onCancel,
}: ConfirmationDialogProps) {
  const [notes, setNotes] = useState("");

  function handleOpenChange(isOpen: boolean) {
    if (!isOpen) {
      onCancel();
    }
  }

  function handleConfirm() {
    onConfirm(notes);
  }

  if (!option) return null;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm Reprotection</DialogTitle>
          <DialogDescription>
            Rebook passengers on flight {option.flight_number}?
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* From line */}
          {originalSegment && (
            <p className="text-sm font-mono">
              From: {originalSegment.flight_number}{" "}
              {originalSegment.origin}-{originalSegment.destination}{" "}
              {originalSegment.departure_time}{" "}
              <Badge variant="cancelled" className="ml-1">CANCELLED</Badge>
            </p>
          )}

          {/* To line */}
          <p className="text-sm font-mono">
            To: {option.flight_number} {option.origin}-{option.destination}{" "}
            {option.departure_time}
          </p>

          <Separator />

          {/* Notes field */}
          <div className="space-y-2">
            <Label htmlFor="operator-notes">Operator Notes</Label>
            <Input
              id="operator-notes"
              placeholder="Optional notes for audit trail"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={loading}
            />
          </div>

          {/* Error display */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Could not record the selection. Please try confirming again.
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={onCancel}
            disabled={loading}
          >
            Back to Options
          </Button>
          <Button onClick={handleConfirm} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Recording decision...
              </>
            ) : (
              "Confirm Selection"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
