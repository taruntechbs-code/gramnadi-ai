interface PlaceholderPageProps {
  title: string
  description: string
}

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <section aria-labelledby="page-title" className="space-y-4">
      <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
        GramNadi AI foundation
      </p>
      <h1 className="text-3xl font-semibold" id="page-title">
        {title}
      </h1>
      <p className="max-w-2xl text-slate-600">{description}</p>
    </section>
  )
}
