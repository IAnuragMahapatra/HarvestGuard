import { useState, useEffect } from 'react';
import TelemetryBar from './components/TelemetryBar';
import AlertFeed from './components/AlertFeed';
import ThreatChain from './components/ThreatChain';
import GraphView from './components/GraphView';
import ShapView from './components/ShapView';
import QuantumRiskPanel from './components/QuantumRiskPanel';
import ProductInfoModal from './components/ProductInfoModal';
import { ArrowLeft, ShieldAlert, Activity, GitCommit, Lock, HelpCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function App() {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [metrics, setMetrics] = useState({
    transactions_analysed: 0,
    cyber_events_ingested: 0,
    correlated_threats: 0,
    quantum_risk_flags: 0
  });
  const [isHelpOpen, setIsHelpOpen] = useState(false);

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
    <div className="h-screen bg-slate-bg text-on-surface selection:bg-electric selection:text-slate-bg font-body overflow-hidden p-4 lg:p-6 flex flex-col">
      
      <header className="flex items-center justify-between mb-6 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-slate-surface p-2 rounded-lg border border-ghost/20 shadow-lg shadow-black/40">
            <ShieldAlert className="w-5 h-5 text-electric" />
          </div>
          <div>
            <h1 className="text-xl font-display tracking-wide font-medium">HarvestGuard</h1>
            <p className="text-ghost text-xs uppercase tracking-widest font-mono">SOC Correlation Engine</p>
          </div>
        </div>
        <button 
          onClick={() => setIsHelpOpen(true)}
          className="flex items-center gap-2 text-ghost hover:text-on-surface transition-colors bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-md border border-white/10 text-sm font-medium"
        >
          <HelpCircle className="w-4 h-4" /> Help
        </button>
      </header>

      <div className="flex-1 min-h-0 relative">
        <AnimatePresence mode="wait">
          {!selectedAlert ? (
            <motion.div
              key="command-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
              className="h-full flex flex-col gap-6"
            >
            {/* Command Center */}
            <div className="shrink-0">
              <TelemetryBar metrics={metrics} />
            </div>

            <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
              <div className="lg:col-span-7 flex flex-col min-w-0 min-h-0">
                <AlertFeed onSelectAlert={setSelectedAlert} />
              </div>
              <div className="lg:col-span-5 flex flex-col min-w-0 min-h-0">
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
            className="h-full flex flex-col gap-6"
          >
            {/* Alert Detail Header */}
            <div className="flex items-center gap-4 shrink-0">
              <button 
                onClick={() => setSelectedAlert(null)}
                className="p-2 bg-slate-surface hover:bg-slate-bg border border-white/5 hover:border-white/20 rounded-full transition-colors group cursor-pointer"
                aria-label="Back to Command Center"
              >
                <ArrowLeft className="w-5 h-5 text-ghost group-hover:text-on-surface transition-colors" />
              </button>
              <h2 className="text-2xl font-display tracking-tight text-on-surface">Alert Analysis: <span className="font-mono text-ghost">{selectedAlert.alert_id}</span></h2>
            </div>

            <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
              <div className="lg:col-span-7 h-full flex flex-col gap-4 min-w-0 min-h-0">
                <ThreatChain alert={selectedAlert} />
                <ShapView alert={selectedAlert} />
              </div>
              <div className="lg:col-span-5 flex flex-col gap-6 min-w-0 min-h-0">
                {selectedAlert.tls_risk_score >= 0.5 && (
                  <div className="shrink-0">
                    <QuantumRiskPanel alert={selectedAlert} />
                  </div>
                )}
                <div className="flex-1 min-h-0 flex flex-col">
                  <GraphView focusAccount={selectedAlert.account_id} alertId={selectedAlert.alert_id} />
                </div>
              </div>
            </section>
          </motion.div>
        )}
        </AnimatePresence>
      </div>
      <ProductInfoModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </div>
  );
}
