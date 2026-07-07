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
    <div className="bg-slate-surface rounded-2xl border border-ghost/10 overflow-hidden shadow-2xl flex flex-col h-[500px]">
      <div className="p-5 border-b border-ghost/10 flex justify-between items-center bg-slate-bg/30">
        <h2 className="text-lg font-display tracking-wide font-medium flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber" /> Live Threat Feed
        </h2>
        <span className="text-xs text-ghost font-mono bg-slate-bg px-2 py-1 rounded">Polling 2s</span>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-auto p-4 custom-scrollbar">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="text-ghost font-medium sticky top-0 bg-slate-surface/90 backdrop-blur pb-2 z-10">
            <tr>
              <th className="pb-3 px-4">Time</th>
              <th className="pb-3 px-4">Score</th>
              <th className="pb-3 px-4">Type</th>
              <th className="pb-3 px-4">Cyber Precursor</th>
              <th className="pb-3 px-4">Financial Pattern</th>
              <th className="pb-3 px-4">Account</th>
              <th className="pb-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ghost/5">
            {alerts.map((alert, idx) => {
              const score = alert.anomaly_score || 0;
              const isCritical = score >= 0.90;
              const isWarning = score >= 0.75 && score < 0.90;
              const isQuantum = alert.tls_risk_score >= 0.5;

              let rowClasses = "hover:bg-slate-bg/50 transition-colors cursor-pointer group";
              let badgeColor = "bg-ghost/10 text-ghost";
              
              if (isCritical) {
                rowClasses += " bg-crimson/5 hover:bg-crimson/10";
                badgeColor = "bg-crimson/20 text-crimson animate-pulse";
              } else if (isWarning) {
                badgeColor = "bg-amber/20 text-amber";
              } else if (isQuantum) {
                rowClasses += " bg-electric/5 hover:bg-electric/10";
                badgeColor = "bg-electric/20 text-electric";
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
                  <td className="py-4 px-4 text-ghost font-mono">{timeStr}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded-md font-mono text-xs font-semibold ${badgeColor}`}>
                      {score.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-4 px-4 font-medium text-on-surface">{isQuantum ? 'Quantum Risk' : 'Correlated Threat'}</td>
                  <td className="py-4 px-4 text-ghost">{precursor || 'None'}</td>
                  <td className="py-4 px-4 text-ghost">{financial || 'None'}</td>
                  <td className="py-4 px-4 font-mono text-xs">{alert.account_id || 'N/A'}</td>
                  <td className="py-4 px-4 text-right">
                    <button className="text-electric group-hover:translate-x-1 transition-transform" aria-label="View Details">
                      <ArrowRight className="w-4 h-4 inline-block" />
                    </button>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
