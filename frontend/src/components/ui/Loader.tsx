export function Loader() {
  return (
    <div className="w-full space-y-4">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="animate-pulse rounded-lg border border-border bg-background p-4"
        >
          <div className="mb-2 h-4 w-3/4 rounded bg-secondary/30" />
          <div className="h-3 w-1/2 rounded bg-secondary/20" />
        </div>
      ))}
    </div>
  )
}
