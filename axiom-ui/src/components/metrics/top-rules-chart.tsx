"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { RuleCount } from "@/lib/types";

interface TopRulesChartProps {
  data: RuleCount[];
}

function humanizeRuleName(rule: string): string {
  return rule
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

const tooltipStyle = {
  backgroundColor: "var(--color-card)",
  borderColor: "var(--color-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--color-foreground)",
};

export function TopRulesChart({ data }: TopRulesChartProps) {
  const formatted = data.map((d) => ({
    ...d,
    label: humanizeRuleName(d.rule),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Top Triggered Rules</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formatted} layout="vertical">
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                opacity={0.3}
                horizontal={false}
              />
              <XAxis
                type="number"
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                width={140}
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar
                dataKey="count"
                fill="var(--color-chart-2)"
                radius={[0, 4, 4, 0]}
                name="Decisions"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
