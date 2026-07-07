import { motion } from 'framer-motion';
import { Shield, Banknote, Lock, ChevronRight } from 'lucide-react';

const mockChainEvents = [
  { id: 'evt-1', time: '10:00:12', type: 'cyber', label: 'Port Scan', source: '10.0.0.99', detail: 'T1046 Network Service Discovery' },
  { id: 'evt-2', time: '10:00:24', type: 'cyber', label: 'Brute Force', source: '10.0.0.99', detail: 'T1110 47 failed attempts' },
  { id: 'evt-3', time: '10:01:13', type: 'cyber', label: 'Login Success', source: '10.0.0.99', detail: 'T1078 Valid Accounts (ACC-0042)' },
  { id: 'evt-4', time: '10:01:27', type: 'transaction', label: 'Transfer Out', source: 'ACC-0042', detail: '₹49,500 to ACC-0071' },
  { id: 'evt-5', time: '10:01:34', type: 'transaction', label: 'Transfer Out', source: 'ACC-0042', detail: '₹49,500 to ACC-0088' }
];

export default function ThreatChain({ alert }) {
  const getIcon = (type) => {
    switch(type) {
      case 'cyber': return <Shield className="w-5 h-5 text-electric" />;
      case 'transaction': return <Banknote className="w-5 h-5 text-amber" />;
      case 'quantum': return <Lock className="w-5 h-5 text-electric" />;
      default: return <Shield className="w-5 h-5 text-ghost" />;
    }
  };

  const getBorderColor = (type) => {
    switch(type) {
      case 'cyber': return 'border-electric';
      case 'transaction': return 'border-amber';
      case 'quantum': return 'border-electric';
      default: return 'border-ghost';
    }
  };

  return (
    <div className="bg-slate-surface rounded-2xl border border-ghost/10 overflow-hidden shadow-2xl p-6">
      <div className="mb-8">
        <h3 className="text-xl font-display font-medium mb-2">Correlation Timeline</h3>
        <p className="text-sm text-ghost font-mono bg-slate-bg inline-block px-3 py-1 rounded border border-ghost/10">
          Attack Chain: {alert.precursor} <ChevronRight className="inline w-3 h-3 mx-1" /> {alert.financial}
        </p>
      </div>

      <div className="relative pt-4 pb-8 overflow-x-auto custom-scrollbar">
        {/* Connecting line background */}
        <div className="absolute top-12 left-8 right-8 h-1 bg-gradient-to-r from-electric via-electric to-amber opacity-30 rounded-full" />
        
        <div className="flex items-start justify-between min-w-max gap-12 px-8 relative z-10">
          {mockChainEvents.map((event, idx) => (
            <motion.div 
              key={event.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
              className="flex flex-col items-center group cursor-pointer"
            >
              <div className="text-xs text-ghost font-mono mb-3">{event.time}</div>
              
              <div className={`w-12 h-12 rounded-full bg-slate-bg flex items-center justify-center border-2 ${getBorderColor(event.type)} shadow-lg shadow-black/50 group-hover:scale-110 transition-transform duration-300 ease-out relative`}>
                {getIcon(event.type)}
                {/* Pulse ring */}
                <div className={`absolute inset-0 rounded-full border border-current opacity-0 group-hover:animate-ping ${event.type === 'cyber' ? 'text-electric' : 'text-amber'}`} />
              </div>

              <div className="mt-4 text-center">
                <div className="font-medium text-sm text-on-surface whitespace-nowrap">{event.label}</div>
                <div className="text-xs text-ghost mt-1 max-w-[120px] leading-tight opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {event.detail}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
