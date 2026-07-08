import { motion, AnimatePresence } from 'framer-motion';
import { X, Info, ShieldAlert, Activity, Lock, GitCommit } from 'lucide-react';

export default function ProductInfoModal({ isOpen, onClose }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0.23, 1, 0.32, 1] }}
            className="bg-slate-surface rounded-xl border border-white/10 shadow-2xl w-full max-w-4xl max-h-full overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-white/5 flex justify-between items-center bg-slate-bg/50 shrink-0">
              <h2 className="text-2xl font-display flex items-center gap-2">
                <Info className="w-6 h-6 text-electric" /> Help & Information
              </h2>
              <button 
                onClick={onClose}
                className="p-2 hover:bg-white/5 rounded-full transition-colors text-ghost hover:text-on-surface"
                aria-label="Close modal"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            {/* Body */}
            <div className="p-8 overflow-y-auto flex-1 text-base text-on-surface/90 space-y-10 custom-scrollbar">
              
              <section className="space-y-3">
                <h3 className="text-xl font-medium font-display text-electric">What is HarvestGuard?</h3>
                <p className="text-ghost leading-relaxed">
                  Think of HarvestGuard as a digital security camera for your financial network. It does not just look at one thing. It watches your standard security logs (like someone trying to guess a password) and compares them instantly with financial transfers (like money moving to a high-risk account). By putting these two pieces together, it spots complex threats before the money is actually gone.
                </p>
              </section>

              <section className="space-y-4">
                <h3 className="text-xl font-medium font-display text-amber">The Four Key Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  <div className="bg-white/5 p-5 rounded-lg border border-white/5">
                    <h4 className="font-medium mb-2 flex items-center gap-2 text-crimson text-lg">
                      <ShieldAlert className="w-5 h-5" /> Correlated Threats
                    </h4>
                    <p className="text-ghost leading-relaxed text-sm">
                      This is our most important metric. It tells you when a suspicious login or network event is directly linked to a risky financial transfer.
                    </p>
                  </div>

                  <div className="bg-white/5 p-5 rounded-lg border border-white/5">
                    <h4 className="font-medium mb-2 flex items-center gap-2 text-electric text-lg">
                      <Lock className="w-5 h-5" /> Quantum Risk (HNDL)
                    </h4>
                    <p className="text-ghost leading-relaxed text-sm">
                      "Harvest Now, Decrypt Later". Attackers are stealing encrypted data now, hoping to crack it later when quantum computers become powerful enough. We flag connections that use weak encryption so you can stop them.
                    </p>
                  </div>

                  <div className="bg-white/5 p-5 rounded-lg border border-white/5">
                    <h4 className="font-medium mb-2 flex items-center gap-2 text-emerald text-lg">
                      <Activity className="w-5 h-5" /> Transactions
                    </h4>
                    <p className="text-ghost leading-relaxed text-sm">
                      The total number of financial transfers we are actively monitoring for signs of fraud or money laundering.
                    </p>
                  </div>

                  <div className="bg-white/5 p-5 rounded-lg border border-white/5">
                    <h4 className="font-medium mb-2 flex items-center gap-2 text-amber text-lg">
                      <GitCommit className="w-5 h-5" /> Cyber Events
                    </h4>
                    <p className="text-ghost leading-relaxed text-sm">
                      The raw security logs (like failed logins or weird network traffic) that we use to build a complete picture of who is doing what.
                    </p>
                  </div>

                </div>
              </section>

              <section className="space-y-4">
                <h3 className="text-xl font-medium font-display text-emerald">Making Sense of the Alert Details</h3>
                <div className="space-y-4 text-ghost bg-slate-bg/30 p-6 rounded-lg border border-white/5">
                  <p>
                    <strong className="text-on-surface">Event Timeline:</strong> A straightforward step-by-step view of how an attack happened.
                  </p>
                  <p>
                    <strong className="text-on-surface">AI Analysis:</strong> Our local AI reads all the complex data and writes a clear, human-readable summary for you.
                  </p>
                  <p>
                    <strong className="text-on-surface">Why this alert fired:</strong> We do not believe in black boxes. This chart shows exactly which factors made our system decide this was a threat.
                  </p>
                  <p>
                    <strong className="text-on-surface">Fraud Ring Topology:</strong> A visual map showing exactly how different accounts and IP addresses are connected to each other.
                  </p>
                </div>
              </section>

            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
