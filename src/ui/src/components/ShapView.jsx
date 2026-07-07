import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bot, BarChart2, Loader2 } from 'lucide-react';

export default function ShapView({ alert }) {
  const [fullAlert, setFullAlert] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!alert?.alert_id) return;
    
    const fetchFullAlert = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/alerts/${alert.alert_id}`);
        if (res.ok) {
          const data = await res.json();
          setFullAlert(data);
        }
      } catch (err) {
        console.error("Failed to fetch full alert details:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchFullAlert();
  }, [alert?.alert_id]);

  const llmReport = alert.llm_report || "No autonomous report generated for this alert.";
  
  // Format SHAP dictionary if present
  let shapFeatures = [];
  try {
    const shapDict = alert.shap_values || {};
    shapFeatures = Object.entries(shapDict)
      .map(([name, value]) => ({ 
        name, 
        value: Number(value) > 0 ? `+${Number(value).toFixed(2)}` : Number(value).toFixed(2) 
      }))
      .sort((a, b) => Math.abs(parseFloat(b.value)) - Math.abs(parseFloat(a.value)))
      .slice(0, 5); // top 5
  } catch (e) {
    // skip
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Autonomous SOC Report */}
      <motion.div 
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="bg-slate-surface rounded-xl border border-white/5 overflow-hidden shadow-xl"
      >
        <div className="p-4 border-b border-white/5 bg-slate-bg/30 flex justify-between items-center">
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
        className="bg-slate-surface rounded-xl border border-white/5 overflow-hidden shadow-xl"
      >
        <div className="p-4 border-b border-white/5 bg-slate-bg/30">
          <h3 className="font-display flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-amber" /> Why did this alert fire?
          </h3>
        </div>
        <div className="p-5">
          {loading ? (
            <div className="h-32 bg-slate-bg rounded-lg border border-ghost/5 mb-4 flex items-center justify-center text-ghost text-sm">
              <Loader2 className="w-6 h-6 animate-spin text-electric" />
            </div>
          ) : fullAlert?.shap_waterfall_png ? (
            <div className="bg-white/90 rounded-lg p-2 mb-4">
              <img 
                src={`data:image/png;base64,${fullAlert.shap_waterfall_png}`} 
                alt="SHAP Waterfall"
                className="w-full h-auto object-contain"
              />
            </div>
          ) : (
            <div className="h-32 bg-slate-bg rounded-lg border border-ghost/5 mb-4 flex items-center justify-center text-ghost text-sm">
              <span>No explainability data available</span>
            </div>
          )}

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
