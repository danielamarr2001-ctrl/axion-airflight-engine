"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, Zap, Clock, TrendingUp } from "lucide-react";
import { fetchMetrics } from "@/lib/api";
import type { MetricsResponse } from "@/lib/types";
import { StatCard } from "@/components/metrics/stat-card";
import { DecisionsTrendChart } from "@/components/metrics/decisions-trend-chart";
import { TopRulesChart } from "@/components/metrics/top-rules-chart";
import { MetricsSkeleton } from "@/components/metrics/metrics-skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function MetricsPage() {
  const { data, isLoading, error } = useQuery<MetricsResponse>({
    queryKey: ["metrics"],
    queryFn: fetchMetrics,
    refetchInterval: 30_000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Metrics</h1>
        <p className="text-sm text-muted-foreground">
          Operational KPI dashboard for decision intelligence.
        </p>
      </div>

      {isLoading && <MetricsSkeleton />}

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Failed to load metrics</AlertTitle>
          <AlertDescription>
            {error instanceof Error
              ? error.message
              : "An unexpected error occurred."}
          </AlertDescription>
        </Alert>
      )}

      {data && data.total_decisions === 0 && (
        <Card>
          <CardContent className="py-10 text-center">
            <p className="text-muted-foreground">
              No decisions recorded yet. Process a PNR through the Processor to
              see metrics here.
            </p>
          </CardContent>
        </Card>
      )}

      {data && data.total_decisions > 0 && (
        <>
          {/* Stat cards row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Decisions"
              value={data.total_decisions}
              icon={Activity}
              description="All time"
            />
            <StatCard
              title="Automation Rate"
              value={data.automation_rate.toFixed(1)}
              unit="%"
              icon={Zap}
              description="Auto-approved decisions"
            />
            <StatCard
              title="Avg Processing Time"
              value={data.avg_processing_time_ms.toFixed(1)}
              unit="ms"
              icon={Clock}
              description="Mean decision latency"
            />
            <StatCard
              title="Recent Day"
              value={
                data.decisions_by_day.length > 0
                  ? data.decisions_by_day[data.decisions_by_day.length - 1]
                      .count
                  : 0
              }
              icon={TrendingUp}
              description="Most recent day"
            />
          </div>

          {/* Charts grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DecisionsTrendChart data={data.decisions_by_day} />
            <TopRulesChart data={data.top_rules} />
          </div>

          {/* Status distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Status Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-8">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Approved</p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-chart-1)" }}
                  >
                    {data.decisions_by_status.APPROVED}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Escalated</p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-chart-4)" }}
                  >
                    {data.decisions_by_status.ESCALATED}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Rejected</p>
                  <p className="text-2xl font-bold text-destructive">
                    {data.decisions_by_status.REJECTED}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
