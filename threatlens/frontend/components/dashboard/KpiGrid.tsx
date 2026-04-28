const cards = [
  ['Total de IOCs', '39', 'Ver lista completa →'],
  ['Casos abertos', '25', 'Ir para casos →'],
  ['Risco crítico', '6', 'Filtrar histórico →'],
  ['Risco alto', '10', 'Filtrar histórico →'],
  ['Risco médio', '13', 'Filtrar histórico →'],
  ['Risco baixo', '10', 'Filtrar histórico →'],
  ['Fontes ativas', '7', 'Saúde das fontes →'],
  ['Última análise', '2026-04-26 07:47:53', 'Abrir detalhe →']
];

export function KpiGrid() {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {cards.map(([title, value, action]) => (
        <button key={title} className="rounded-xl border border-cyan/30 bg-surface p-4 text-left hover:border-cyan/70">
          <div className="text-2xl font-bold">{value}</div>
          <div className="text-sm text-slate-200">{title}</div>
          <div className="text-xs text-slate-400 mt-2">{action}</div>
        </button>
      ))}
    </section>
  );
}
