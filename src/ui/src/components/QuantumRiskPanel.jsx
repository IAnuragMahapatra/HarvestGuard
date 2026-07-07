import { motion } from 'framer-motion';
import { LockKeyhole } from 'lucide-react';

export default function QuantumRiskPanel({ alert }) {
  const score = alert.tls_risk_score || 0;
  const percentage = Math.round(score * 100);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="bg-electric/10 rounded-xl border border-electric/30 overflow-hidden shadow-xl"
    >
      <div className="p-4 border-b border-electric/20 bg-electric/5 flex justify-between items-center">
        <h3 className="font-display flex items-center gap-2 text-electric">
          <LockKeyhole className="w-5 h-5" /> Quantum Exposure (HNDL)
        </h3>
      </div>
      <div className="p-5 flex flex-col gap-4">
        {/* Progress Bar */}
        <div className="w-full bg-slate-bg rounded-full h-2.5 border border-white/5 overflow-hidden">
          <div 
            className="bg-electric h-2.5 rounded-full transition-all duration-1000 ease-out" 
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        <div className="text-sm font-mono text-ghost flex justify-between">
          <span>Risk Score: {score.toFixed(2)}</span>
          <span className="text-electric">Threshold: 0.50</span>
        </div>

        <div className="text-sm text-on-surface/90 mt-2 p-3 bg-electric/5 rounded border border-electric/10">
          {alert.mitre_tags?.includes("T1573") 
            ? "PQC Downgrade Attack detected. Adversary forced connection downgrade to vulnerable cipher suite during internal session."
            : "This session used RSA-2048 (vulnerable to quantum attack) and transferred massive data to an unverified ASN. This matches a Harvest Now Decrypt Later exfiltration pattern."}
        </div>
      </div>
    </motion.div>
  );
}
