import { motion } from 'framer-motion';

export default function MetricTile({ title, value, icon: Icon, color, delay }) {
  // Mapping color prop to tailwind text color class for the icon
  const colorMap = {
    emerald: 'text-emerald',
    electric: 'text-electric',
    crimson: 'text-crimson'
  };

  const iconColor = colorMap[color] || 'text-ghost';
  const bgColor = {
    emerald: 'bg-emerald/10 text-emerald',
    electric: 'bg-electric/10 text-electric',
    crimson: 'bg-crimson/10 text-crimson'
  }[color] || 'bg-ghost/10 text-ghost';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1], delay }}
      className="bg-slate-surface rounded-xl p-6 border border-white/5 shadow-2xl relative overflow-hidden group"
    >
      {/* Premium hardware inset shadow */}
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] rounded-xl" />
      
      <div className="flex justify-between items-start mb-6 relative z-10">
        <h3 className="text-ghost text-xs font-mono tracking-widest uppercase">{title}</h3>
        <div className={`p-2.5 rounded-lg border border-white/5 shadow-inner backdrop-blur-md ${bgColor}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      
      <div className="relative z-10">
        <span className="text-4xl font-display tracking-tight text-on-surface">
          {value.toLocaleString()}
        </span>
      </div>

      {/* Hardware LED glow effect */}
      <div className={`absolute -top-12 -right-12 w-32 h-32 opacity-20 blur-[40px] pointer-events-none ${bgColor.split(' ')[0].replace('/10', '')}`} />
      
      {/* Decorative scanline on hover */}
      <div className="absolute inset-0 translate-y-[100%] group-hover:translate-y-[-100%] bg-gradient-to-b from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-1000 ease-in-out pointer-events-none" />
    </motion.div>
  );
}
