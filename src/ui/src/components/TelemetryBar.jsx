import { motion } from 'framer-motion';
import { Activity, GitCommit, ShieldAlert, Lock } from 'lucide-react';

export default function TelemetryBar({ metrics }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
      className="bg-slate-surface rounded-xl border border-white/5 shadow-2xl relative overflow-hidden flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-white/10"
    >
      {/* Subtle inset highlight */}
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] rounded-xl z-20" />

      {/* Metric 1: Transactions Analysed */}
      <div className="flex-1 p-4 lg:p-5 relative group">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-ghost text-xs font-mono tracking-widest uppercase">Transactions</h3>
          <Activity className="w-5 h-5 text-emerald opacity-70" />
        </div>
        <div className="text-3xl lg:text-4xl font-display tracking-tight text-on-surface">
          {metrics.transactions_analysed.toLocaleString()}
        </div>
      </div>

      {/* Metric 2: Cyber Events */}
      <div className="flex-1 p-4 lg:p-5 relative group">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-ghost text-xs font-mono tracking-widest uppercase">Events Ingested</h3>
          <GitCommit className="w-5 h-5 text-electric opacity-70" />
        </div>
        <div className="text-3xl lg:text-4xl font-display tracking-tight text-on-surface">
          {metrics.cyber_events_ingested.toLocaleString()}
        </div>
      </div>

      {/* Metric 3: Correlated Threats (Highlighted) */}
      <div className="flex-1 p-4 lg:p-5 relative bg-crimson/5">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-crimson text-xs font-mono tracking-widest uppercase font-semibold flex items-center gap-2">
            <ShieldAlert className="w-4 h-4" /> Correlated Threats
          </h3>
        </div>
        <div className="text-4xl lg:text-5xl font-display tracking-tight text-crimson">
          {metrics.correlated_threats.toLocaleString()}
        </div>
      </div>

      {/* Metric 4: Quantum Risk Flags (Highlighted) */}
      <div className="flex-1 p-4 lg:p-5 relative bg-electric/5">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-electric text-xs font-mono tracking-widest uppercase font-semibold flex items-center gap-2">
            <Lock className="w-4 h-4" /> Quantum Risk
          </h3>
        </div>
        <div className="text-4xl lg:text-5xl font-display tracking-tight text-electric">
          {metrics.quantum_risk_flags.toLocaleString()}
        </div>
      </div>
    </motion.div>
  );
}
