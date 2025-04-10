"use client"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function ProgressTracker({ value, label }: { value: number; label: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <Progress value={value} className="h-2" />
        <p className="text-xs text-muted-foreground mt-2">{Math.round(value)}% complete</p>
      </CardContent>
    </Card>
  )
}
