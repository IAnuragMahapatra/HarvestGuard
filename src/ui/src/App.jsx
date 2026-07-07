import { useState, useEffect } from 'react';
import MetricTile from './components/MetricTile';
import AlertFeed from './components/AlertFeed';
import ThreatChain from './components/ThreatChain';
import GraphView from './components/GraphView';
import ShapView from './components/ShapView';
import QuantumRiskPanel from './components/QuantumRiskPanel';
import { ArrowLeft, ShieldAlert, Activity, GitCommit, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function App() {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [metrics, setMetrics] = useState({
    transactions_analysed: 0,
    cyber_events_ingested: 0,
    correlated_threats: 0,
    quantum_risk_flags: 0
  });

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const res = await fetch('/api/counts');
        if (res.ok) {
          const data = await res.json();
          setMetrics(data);
        }
      } catch (err) {
        console.error("Failed to fetch counts:", err);
      }
    };
    
    fetchCounts();
    const interval = setInterval(fetchCounts, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-bg text-on-surface selection:bg-electric selection:text-slate-bg font-body overflow-x-hidden p-6 lg:p-10">
      
      <header className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-3">
          <div className="bg-slate-surface p-3 rounded-lg border border-ghost/20 shadow-lg shadow-black/40">
            <ShieldAlert className="w-6 h-6 text-electric" />
          </div>
          <div>
            <h1 className="text-2xl font-display tracking-wide font-medium">HarvestGuard</h1>
            <p className="text-ghost text-sm uppercase tracking-widest font-mono">SOC Correlation Engine</p>
          </div>
        </div>
      </header>

      <AnimatePresence mode="wait">
        {!selectedAlert ? (
          <motion.div
            key="command-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
          >
            {/* Command Center */}
            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
              <MetricTile title="Transactions Analysed" value={metrics.transactions_analysed} icon={Activity} color="emerald" delay={0.1} />
              <MetricTile title="Cyber Events Ingested" value={metrics.cyber_events_ingested} icon={GitCommit} color="electric" delay={0.2} />
              <MetricTile title="Correlated Threats" value={metrics.correlated_threats} icon={ShieldAlert} color="crimson" delay={0.3} />
              <MetricTile title="Quantum Risk Flags" value={metrics.quantum_risk_flags} icon={Lock} color="electric" delay={0.4} />
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-7">
                <AlertFeed onSelectAlert={setSelectedAlert} />
              </div>
              <div className="lg:col-span-5 bg-slate-surface rounded-xl border border-white/5 overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
                <GraphView />
              </div>
            </section>
          </motion.div>
        ) : (
          <motion.div
            key="alert-detail"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
            className="flex flex-col gap-8"
          >
            {/* Alert Detail Header */}
            <div className="flex items-center gap-4">
              <button 
                onClick={() => setSelectedAlert(null)}
                className="p-2 bg-slate-surface hover:bg-slate-bg border border-white/5 hover:border-white/20 rounded-full transition-colors group cursor-pointer"
                aria-label="Back to Command Center"
              >
                <ArrowLeft className="w-5 h-5 text-ghost group-hover:text-on-surface transition-colors" />
              </button>
              <h2 className="text-2xl font-display tracking-tight text-on-surface">Alert Analysis: <span className="font-mono text-ghost">{selectedAlert.alert_id}</span></h2>
            </div>

            <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-7 flex flex-col gap-8">
                <ThreatChain alert={selectedAlert} />
                <ShapView alert={selectedAlert} />
              </div>
              <div className="lg:col-span-5 flex flex-col gap-8">
                {selectedAlert.tls_risk_score >= 0.5 && (
                  <QuantumRiskPanel alert={selectedAlert} />
                )}
                <div className="bg-slate-surface rounded-xl border border-white/5 shadow-[0_8px_32px_rgba(0,0,0,0.4)] overflow-hidden h-[400px]">
                  {/* Additional context or graph could go here */}
                  <GraphView focusAccount={selectedAlert.account_id} alertId={selectedAlert.alert_id} />
                </div>
              </div>
            </section>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
