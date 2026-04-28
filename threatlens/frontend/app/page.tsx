import { Topbar } from '../components/layout/Topbar';
import { KpiGrid } from '../components/dashboard/KpiGrid';

export default function HomePage() {
  return (
    <main className="mx-auto max-w-7xl p-4 space-y-4">
      <Topbar />
      <section className="rounded-xl border border-cyan/30 bg-surface p-3 text-sm text-slate-300">● Operacional • Ambiente: Produção • v1.3.0 • Últimas 24h • Fontes: 7</section>
      <section className="rounded-xl border border-cyan/30 bg-surface p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div><h1 className="text-3xl font-bold">ThreatLens</h1><p className="text-slate-400">IOC Enrichment & Triage Platform</p></div>
        <button className="rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 px-4 py-2 font-semibold">Analisar IOC</button>
      </section>
      <section className="rounded-xl border border-cyan/30 bg-surface p-3"><input className="w-full rounded-lg bg-surface2 border border-cyan/30 px-3 py-2" placeholder="Buscar IOC, domínio, IP, hash ou caso..." /></section>
      <KpiGrid />
      <footer className="text-center text-slate-400 py-4">Desenvolvido por <span className="text-cyan-400">Patrick Santos</span></footer>
    </main>
  );
}
