"use client";

import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

export function ProgressBar({
  currentStep,
  totalSteps,
  label,
  className,
}: {
  currentStep: number;
  totalSteps: number;
  label?: string;
  className?: string;
}) {
  const safeTotal = Math.max(1, totalSteps);
  const percentage = Math.min(100, Math.max(0, Math.round((currentStep / safeTotal) * 100)));

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between text-xs text-zinc-400">
        <span>{label ?? "Progress"}</span>
        <span>{percentage}%</span>
      </div>
      <Progress
        aria-label={label ?? "Progress"}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percentage}
        value={percentage}
      />
    </div>
  );
}
