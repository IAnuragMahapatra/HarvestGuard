import { motion } from 'framer-motion';
import { ArrowRight, Zap, ShieldAlert, GitBranch } from 'lucide-react';

// Mock data to simulate alerts from the backend
const mockAlerts = [
  { id: 'ALT-1049', time: '10:06:21', score: 0.94, type: 'Correlated Threat', precursor: 'T1110 Brute Force', financial: 'FATF-3 Smurfing', account: 'ACC-0042', tls_risk_score: 0.1 },
  { id: 'ALT-1048', time: '10:01:14', score: 0.82, type: 'Velocity Anomaly', precursor: 'None', financial: 'High Velocity', account: 'ACC-0891', tls_risk_score: 0.0 },
  { id: 'ALT-1047', time: '09:55:03', score: 0.65, type: 'Quantum Risk', precursor: 'HNDL Pattern', financial: 'None', account: 'SYS-NET', tls_risk_score: 0.85 },
  { id: 'ALT-1046', time: '09:42:11', score: 0.91, type: 'Correlated Threat', precursor: 'T1078 Valid Accounts', financial: 'Mule Transfer', account: 'ACC-0071', tls_risk_score: 0.0 }
];

export default function AlertFeed({ onSelectAlert }) {
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
            {mockAlerts.map((alert, idx) => {
              const isCritical = alert.score >= 0.90;
              const isWarning = alert.score >= 0.75 && alert.score < 0.90;
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

              return (
                <motion.tr 
                  key={alert.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => onSelectAlert(alert)}
                  className={rowClasses}
                >
                  <td className="py-4 px-4 text-ghost font-mono">{alert.time}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded-md font-mono text-xs font-semibold ${badgeColor}`}>
                      {alert.score.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-4 px-4 font-medium text-on-surface">{alert.type}</td>
                  <td className="py-4 px-4 text-ghost">{alert.precursor}</td>
                  <td className="py-4 px-4 text-ghost">{alert.financial}</td>
                  <td className="py-4 px-4 font-mono text-xs">{alert.account}</td>
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
