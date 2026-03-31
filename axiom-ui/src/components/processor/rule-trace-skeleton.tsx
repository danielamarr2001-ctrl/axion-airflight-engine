import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const STEP_OPACITIES = ["opacity-80", "opacity-60", "opacity-40", "opacity-30", "opacity-20"];

export function RuleTraceSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {STEP_OPACITIES.map((opacity, i) => (
            <div key={i} className={`flex items-center gap-3 ${opacity}`}>
              <Skeleton className="h-4 w-4 rounded-full" />
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-5 w-12" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
