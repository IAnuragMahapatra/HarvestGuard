import { motion } from 'framer-motion';

export default function MetricTile({ title, value, icon: Icon, color, delay }) {
  // Mapping color prop to tailwind text color class for the icon
  const colorMap = {
    emerald: 'text-emerald',
    electric: 'text-electric',
    crimson: 'text-crimson'
  };

  const iconColor = colorMap[color] || 'text-ghost';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1], delay }}
      className="bg-slate-surface rounded-2xl p-6 border border-ghost/10 shadow-lg relative overflow-hidden group"
    >
      <div className="flex justify-between items-start mb-4 relative z-10">
        <h3 className="text-ghost text-sm font-medium tracking-wide">{title}</h3>
        <div className={`p-2 bg-slate-bg/50 rounded-lg border border-ghost/5 ${iconColor}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      
      <div className="relative z-10">
        <span className="text-3xl font-mono font-semibold tracking-tight text-on-surface">
          {value.toLocaleString()}
        </span>
      </div>

      {/* Decorative gradient orb on hover */}
      <div className="absolute -bottom-8 -right-8 w-32 h-32 bg-current opacity-0 group-hover:opacity-5 blur-2xl transition-opacity duration-500 pointer-events-none" style={{ color: `var(--color-${color})` }} />
    </motion.div>
  );
}
