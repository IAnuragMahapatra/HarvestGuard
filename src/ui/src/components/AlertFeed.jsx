import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Zap, ShieldAlert, GitBranch } from 'lucide-react';

export default function AlertFeed({ onSelectAlert }) {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch('/api/alerts?limit=50');
        if (res.ok) {
          const data = await res.json();
          setAlerts(data);
        }
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
      }
    };
    
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 2000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="bg-slate-surface rounded-xl border border-white/5 overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.4)] flex flex-col flex-1 min-h-0 relative">
      {/* Subtle inset highlight for premium feel */}
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] rounded-xl z-20" />
      
      <div className="p-4 border-b border-white/5 flex justify-between items-center bg-black/20 backdrop-blur-sm relative z-10 shrink-0">
        <h2 className="text-xl font-display tracking-wide font-medium flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber" /> Live Alerts
        </h2>
        <span className="text-xs text-ghost font-mono bg-slate-bg px-2 py-1 rounded">Polling 2s</span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 custom-scrollbar">
        <table className="w-full text-left text-sm">
          <thead className="text-ghost font-medium">
            <tr>
              <th className="sticky top-0 bg-slate-surface z-20 pt-4 pb-3 px-4 border-b border-white/5 shadow-sm">Time</th>
              <th className="sticky top-0 bg-slate-surface z-20 pt-4 pb-3 px-4 border-b border-white/5 shadow-sm">Score</th>
              <th className="sticky top-0 bg-slate-surface z-20 pt-4 pb-3 px-4 border-b border-white/5 shadow-sm">Type</th>
              <th className="sticky top-0 bg-slate-surface z-20 pt-4 pb-3 px-4 border-b border-white/5 shadow-sm">Cyber Precursor</th>
              <th className="sticky top-0 bg-slate-surface z-20 pt-4 pb-3 px-4 border-b border-white/5 shadow-sm">Financial Pattern</th>
              <th className="sticky top-0 bg-slate-surface z-20 pt-4 pb-3 px-4 text-right border-b border-white/5 shadow-sm">Account</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ghost/5">
            {alerts.map((alert, idx) => {
              const score = alert.anomaly_score || 0;
              const isCritical = score >= 0.90;
              const isWarning = score >= 0.75 && score < 0.90;
              const isQuantum = alert.tls_risk_score >= 0.5;

              let rowClasses = "hover:bg-white/5 transition-colors cursor-pointer group relative";
              let badgeColor = "bg-white/5 text-ghost border border-white/10";
              
              if (isCritical) {
                rowClasses += " bg-crimson/5 hover:bg-crimson/10";
                badgeColor = "bg-crimson/20 text-crimson border border-crimson/30 shadow-[0_0_10px_rgba(229,57,53,0.3)] animate-pulse";
              } else if (isWarning) {
                rowClasses += " bg-amber/5 hover:bg-amber/10";
                badgeColor = "bg-amber/20 text-amber border border-amber/30";
              } else if (isQuantum) {
                rowClasses += " bg-electric/5 hover:bg-electric/10";
                badgeColor = "bg-electric/20 text-electric border border-electric/30";
              }

              // format time HH:MM:SS
              const timeStr = alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : '--:--:--';
              const precursor = alert.mitre_tags ? alert.mitre_tags.join(', ') : 'None';
              const financial = alert.fatf_tags ? alert.fatf_tags.join(', ') : 'None';

              return (
                <motion.tr 
                  key={alert.alert_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => onSelectAlert(alert)}
                  className={rowClasses}
                >
                  <td className="py-4 px-4 text-ghost font-mono whitespace-nowrap">{timeStr}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded-md font-mono text-xs font-semibold ${badgeColor}`}>
                      {score.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-4 px-4 font-medium text-on-surface">{isQuantum ? 'Quantum Risk' : 'Correlated Threat'}</td>
                  <td className="py-4 px-4 text-ghost">{precursor || 'None'}</td>
                  <td className="py-4 px-4 text-ghost">{financial || 'None'}</td>
                  <td className="py-4 px-4 font-mono text-xs whitespace-nowrap">{alert.account_id || 'N/A'}</td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
