import { motion } from 'framer-motion';
import { Bot, BarChart2 } from 'lucide-react';

export default function ShapView({ alert }) {
  // Mock LLM report and SHAP features
  const llmReport = "CRITICAL: IP 10.0.0.99 executed MITRE T1110 (Brute Force) 61 seconds before successful authentication. Three structuring transfers totalling ₹1,48,500 followed immediately. This sequence is highly consistent with FATF Typology 3 (Smurfing). Recommend immediate account freeze and SOC escalation.";
  
  const shapFeatures = [
    { name: 'prior_cyber_alert_count', value: '+0.41' },
    { name: 'transfer_velocity_3min', value: '+0.31' },
    { name: 'ip_reputation_score', value: '+0.19' }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Autonomous SOC Report */}
      <motion.div 
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="bg-slate-surface rounded-2xl border border-ghost/10 overflow-hidden shadow-xl"
      >
        <div className="p-4 border-b border-ghost/10 bg-slate-bg/30 flex justify-between items-center">
          <h3 className="font-display flex items-center gap-2">
            <Bot className="w-5 h-5 text-electric" /> Autonomous SOC Report
          </h3>
          <span className="text-[10px] uppercase tracking-wider text-electric border border-electric/30 px-2 py-1 rounded bg-electric/10">Local AI Data</span>
        </div>
        <div className="p-5 text-sm leading-relaxed text-on-surface/90 font-body">
          {llmReport}
        </div>
      </motion.div>

      {/* Explainability / SHAP */}
      <motion.div 
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="bg-slate-surface rounded-2xl border border-ghost/10 overflow-hidden shadow-xl"
      >
        <div className="p-4 border-b border-ghost/10 bg-slate-bg/30">
          <h3 className="font-display flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-amber" /> Why did this alert fire?
          </h3>
        </div>
        <div className="p-5">
          {/* Mock Waterfall Plot visual representation */}
          <div className="h-32 bg-slate-bg rounded-lg border border-ghost/5 mb-4 flex items-center justify-center text-ghost text-sm relative overflow-hidden">
            <div className="absolute top-4 left-8 h-4 bg-crimson w-32 rounded-r opacity-80" />
            <div className="absolute top-12 left-8 h-4 bg-crimson w-24 rounded-r opacity-80" />
            <div className="absolute top-20 left-8 h-4 bg-crimson w-16 rounded-r opacity-80" />
            <span className="z-10 bg-slate-bg/80 px-2 rounded backdrop-blur-sm">[SHAP Waterfall Plot renders here]</span>
          </div>

          <div className="space-y-2">
            {shapFeatures.map((feat, idx) => (
              <div key={idx} className="flex justify-between items-center text-xs font-mono border-b border-ghost/5 pb-2">
                <span className="text-ghost">{feat.name}</span>
                <span className="text-crimson font-medium">{feat.value}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
