"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DailyDecisions } from "@/lib/types";

interface DecisionsTrendChartProps {
  data: DailyDecisions[];
}

function formatChartDate(dateStr: string): string {
  const [, month, day] = dateStr.split("-");
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  return `${months[parseInt(month, 10) - 1]} ${parseInt(day, 10)}`;
}

const tooltipStyle = {
  backgroundColor: "var(--color-card)",
  borderColor: "var(--color-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--color-foreground)",
};

export function DecisionsTrendChart({ data }: DecisionsTrendChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Decisions per Day</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                opacity={0.3}
              />
              <XAxis
                dataKey="date"
                tickFormatter={formatChartDate}
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={{ stroke: "var(--color-border)" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={formatChartDate}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="approved"
                stackId="1"
                stroke="var(--color-chart-1)"
                fill="var(--color-chart-1)"
                fillOpacity={0.4}
                name="Approved"
              />
              <Area
                type="monotone"
                dataKey="escalated"
                stackId="1"
                stroke="var(--color-chart-4)"
                fill="var(--color-chart-4)"
                fillOpacity={0.4}
                name="Escalated"
              />
              <Area
                type="monotone"
                dataKey="rejected"
                stackId="1"
                stroke="var(--color-destructive)"
                fill="var(--color-destructive)"
                fillOpacity={0.4}
                name="Rejected"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
