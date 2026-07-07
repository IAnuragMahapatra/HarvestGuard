import { motion } from 'framer-motion';
import { Network } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function GraphView({ focusAccount }) {
  // Mock data for the network graph representing a fraud ring
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}'
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: [
          { id: '0', name: '10.0.0.99 (Attacker IP)', symbolSize: 30, itemStyle: { color: '#29B6F6' } },
          { id: '1', name: 'ACC-0042 (Compromised)', symbolSize: 45, itemStyle: { color: '#E53935' } },
          { id: '2', name: 'ACC-0071 (Mule)', symbolSize: 25, itemStyle: { color: '#FFB300' } },
          { id: '3', name: 'ACC-0088 (Mule)', symbolSize: 25, itemStyle: { color: '#FFB300' } },
          { id: '4', name: 'ACC-0103 (Mule)', symbolSize: 25, itemStyle: { color: '#FFB300' } },
          { id: '5', name: '192.168.1.15', symbolSize: 20, itemStyle: { color: '#00E676' } },
          { id: '6', name: 'ACC-0891', symbolSize: 20, itemStyle: { color: '#00E676' } }
        ],
        links: [
          { source: '0', target: '1', lineStyle: { color: '#8892A4', width: 2, type: 'dashed' } },
          { source: '1', target: '2', lineStyle: { color: '#FFB300', width: 3 } },
          { source: '1', target: '3', lineStyle: { color: '#FFB300', width: 3 } },
          { source: '1', target: '4', lineStyle: { color: '#FFB300', width: 3 } },
          { source: '5', target: '6', lineStyle: { color: '#8892A4', width: 1 } }
        ],
        roam: true,
        label: {
          show: true,
          position: 'right',
          color: '#8892A4',
          fontSize: 10
        },
        force: {
          repulsion: 300,
          edgeLength: 80
        }
      }
    ]
  };

  return (
    <div className="h-full min-h-[400px] flex flex-col">
      <div className="p-5 border-b border-ghost/10 flex justify-between items-center bg-slate-bg/30">
        <h2 className="text-lg font-display tracking-wide font-medium flex items-center gap-2">
          <Network className="w-5 h-5 text-ghost" /> Fraud Ring Topology
        </h2>
      </div>
      <div className="flex-1 p-4 relative">
        <ReactECharts 
          option={option} 
          style={{ height: '100%', width: '100%' }}
          opts={{ renderer: 'canvas' }}
        />
        {/* Subtle overlay vignette */}
        <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_50px_rgba(30,36,48,0.8)] rounded-b-2xl" />
      </div>
    </div>
  );
}
