"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { BookOpen } from "lucide-react";

interface RuleSchema {
  id: number;
  field: string;
  operator: string;
  value: string;
  action: string;
  priority: number;
  active: boolean;
  created_at: string;
}

function humanizeFieldName(field: string): string {
  return field
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function humanizeOperator(op: string): string {
  const labels: Record<string, string> = {
    "=": "equals",
    ">": "greater than",
    "<": "less than",
    ">=": "at least",
    "<=": "at most",
    missing: "is missing",
  };
  return labels[op] ?? op;
}

function RulesSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-5 w-16 rounded-md" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function RulesPage() {
  const { data: rules, isLoading, error } = useQuery<RuleSchema[]>({
    queryKey: ["rules"],
    queryFn: () => apiFetch<RuleSchema[]>("/rules"),
  });

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">Active Rules</h1>
          {rules && (
            <Badge variant="secondary" className="text-xs">
              {rules.length} {rules.length === 1 ? "rule" : "rules"}
            </Badge>
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          Business rules governing the decision engine.
        </p>
      </div>

      {isLoading && <RulesSkeleton />}

      {error && (
        <Card>
          <CardContent className="py-10 text-center">
            <p className="text-muted-foreground">
              Failed to load rules. Ensure the backend is running.
            </p>
          </CardContent>
        </Card>
      )}

      {rules && rules.length === 0 && (
        <Card>
          <CardContent className="py-10 text-center">
            <BookOpen className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">
              No active rules configured. Seed the database to populate rules.
            </p>
          </CardContent>
        </Card>
      )}

      {rules && rules.length > 0 && (
        <div className="animate-in fade-in duration-200">
          <Card>
            <CardContent className="pt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Field</TableHead>
                    <TableHead>Operator</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead className="text-right">Priority</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-medium">
                        {humanizeFieldName(rule.field)}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {humanizeOperator(rule.operator)}
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {rule.value || "\u2014"}
                      </TableCell>
                      <TableCell>{humanizeFieldName(rule.action)}</TableCell>
                      <TableCell className="text-right">{rule.priority}</TableCell>
                      <TableCell>
                        <Badge variant={rule.active ? "approved" : "secondary"}>
                          {rule.active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
