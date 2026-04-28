const items = ['Painel', 'Analisar IOC', 'Análise em Lote', 'Histórico', 'Casos', 'Configurações', 'Sobre'];

export function Topbar() {
  return (
    <header className="rounded-xl border border-cyan/30 bg-surface p-3">
      <div className="flex items-center gap-4 overflow-x-auto whitespace-nowrap">
        <div className="font-semibold text-cyan text-lg">ThreatLens</div>
        {items.map((item, idx) => (
          <button key={item} className={`rounded-lg px-3 py-2 text-sm ${idx === 0 ? 'bg-cyan/20 text-white border border-cyan/60' : 'text-slate-300 hover:text-white'}`}>
            {item}
          </button>
        ))}
      </div>
    </header>
  );
}
