import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        approved: "border-[oklch(0.72_0.15_185/0.3)] bg-[oklch(0.72_0.15_185/0.15)] text-primary",
        rejected: "border-[oklch(0.55_0.2_25/0.3)] bg-[oklch(0.55_0.2_25/0.15)] text-destructive",
        escalated: "border-[oklch(0.7_0.15_55/0.3)] bg-[oklch(0.7_0.15_55/0.15)] text-[var(--color-chart-4)]",
        scheduled: "border-[oklch(0.72_0.15_185/0.3)] bg-[oklch(0.72_0.15_185/0.15)] text-primary",
        cancelled: "border-[oklch(0.55_0.2_25/0.3)] bg-[oklch(0.55_0.2_25/0.15)] text-destructive",
        confirmed: "border-[oklch(0.7_0.15_145/0.3)] bg-[oklch(0.7_0.15_145/0.15)] text-[var(--color-chart-3)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
