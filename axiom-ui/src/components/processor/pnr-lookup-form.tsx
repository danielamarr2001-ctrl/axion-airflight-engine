"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

interface PnrLookupFormProps {
  onSubmit: (pnr: string, lastName: string) => void;
  disabled?: boolean;
  loading?: boolean;
}

export function PnrLookupForm({ onSubmit, disabled, loading }: PnrLookupFormProps) {
  const [pnr, setPnr] = useState("");
  const [lastName, setLastName] = useState("");

  const canSubmit = pnr.trim().length > 0 && lastName.trim().length > 0 && !disabled;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onSubmit(pnr.trim().toUpperCase(), lastName.trim().toUpperCase());
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2 max-w-md">
      <div className="flex-1 space-y-1.5">
        <Label htmlFor="pnr-code" className="text-xs">PNR Code</Label>
        <Input
          id="pnr-code"
          placeholder="e.g. XKJR4T"
          maxLength={6}
          className="uppercase font-mono"
          value={pnr}
          onChange={(e) => setPnr(e.target.value)}
          disabled={disabled}
        />
      </div>
      <div className="flex-1 space-y-1.5">
        <Label htmlFor="last-name" className="text-xs">Last Name</Label>
        <Input
          id="last-name"
          placeholder="e.g. MARTINEZ"
          className="uppercase"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          disabled={disabled}
        />
      </div>
      <Button type="submit" disabled={!canSubmit || loading}>
        {loading ? (
          <>
            <Loader2 className="animate-spin h-4 w-4 mr-2" />
            Looking up...
          </>
        ) : (
          "Look Up"
        )}
      </Button>
    </form>
  );
}
