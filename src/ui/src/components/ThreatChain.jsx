import { motion } from 'framer-motion';
import { Shield, Banknote, Lock, ChevronRight } from 'lucide-react';



export default function ThreatChain({ alert }) {
  const getIcon = (type, tlsRiskScore) => {
    if (tlsRiskScore >= 0.5) return <Lock className="w-5 h-5 text-electric" />;
    switch(type) {
      case 'cyber': return <Shield className="w-5 h-5 text-electric" />;
      case 'transaction': return <Banknote className="w-5 h-5 text-amber" />;
      default: return <Shield className="w-5 h-5 text-ghost" />;
    }
  };

  const getBorderColor = (type, tlsRiskScore) => {
    if (tlsRiskScore >= 0.5) return 'border-electric';
    switch(type) {
      case 'cyber': return 'border-electric';
      case 'transaction': return 'border-amber';
      default: return 'border-ghost';
    }
  };

  const threatChain = alert.threat_chain || [];
  const mitreTags = alert.mitre_tags ? alert.mitre_tags.join(', ') : 'None';
  const fatfTags = alert.fatf_tags ? alert.fatf_tags.join(', ') : 'None';

  return (
    <div className="bg-slate-surface rounded-2xl border border-ghost/10 overflow-hidden shadow-2xl p-6">
      <div className="mb-8">
        <h3 className="text-xl font-display font-medium mb-2">Correlation Timeline</h3>
        <p className="text-sm text-ghost font-mono bg-slate-bg inline-block px-3 py-1 rounded border border-ghost/10">
          Attack Chain: {mitreTags} <ChevronRight className="inline w-3 h-3 mx-1" /> {fatfTags}
        </p>
      </div>

      <div className="relative pt-4 pb-8 overflow-x-auto custom-scrollbar">
        {/* Connecting line background */}
        <div className="absolute top-12 left-8 right-8 h-1 bg-gradient-to-r from-electric via-electric to-amber opacity-30 rounded-full" />
        
        <div className="flex items-start justify-between min-w-max gap-12 px-8 relative z-10">
          {threatChain.map((event, idx) => {
            const timeStr = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : '--:--:--';
            
            let label = 'Event';
            let detail = '';
            if (event.type === 'cyber') {
              label = event.event_type || 'Cyber Event';
              detail = event.mitre_tag || '';
            } else if (event.type === 'transaction') {
              label = 'Transfer';
              detail = event.amount_inr ? `₹${event.amount_inr}` : (event.fatf_tag || '');
            }

            return (
              <motion.div 
                key={event.event_id || idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1, duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
                className="flex flex-col items-center group cursor-pointer"
              >
                <div className="text-xs text-ghost font-mono mb-3">{timeStr}</div>
                
                <div className={`w-12 h-12 rounded-full bg-slate-bg flex items-center justify-center border-2 ${getBorderColor(event.type, alert.tls_risk_score)} shadow-lg shadow-black/50 group-hover:scale-110 transition-transform duration-300 ease-out relative`}>
                  {getIcon(event.type, alert.tls_risk_score)}
                  {/* Pulse ring */}
                  <div className={`absolute inset-0 rounded-full border border-current opacity-0 group-hover:animate-ping ${event.type === 'cyber' ? 'text-electric' : 'text-amber'}`} />
                </div>

                <div className="mt-4 text-center">
                  <div className="font-medium text-sm text-on-surface whitespace-nowrap">{label}</div>
                  <div className="text-xs text-ghost mt-1 max-w-[120px] leading-tight opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    {detail}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
