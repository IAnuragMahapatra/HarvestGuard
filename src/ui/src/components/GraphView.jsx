import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Network, Loader2 } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function GraphView({ focusAccount, alertId }) {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      try {
        let targetAlertId = alertId;
        
        // If no alertId is provided (e.g. on the Command Center dashboard),
        // fetch the most recent alert to display its graph.
        if (!targetAlertId) {
          const alertsRes = await fetch('/api/alerts?limit=1');
          if (alertsRes.ok) {
            const alerts = await alertsRes.json();
            if (alerts.length > 0) {
              targetAlertId = alerts[0].alert_id;
            }
          }
        }
        
        if (targetAlertId) {
          const res = await fetch(`/api/alerts/${targetAlertId}/graph`);
          if (res.ok) {
            const data = await res.json();
            setGraphData(data);
          }
        }
      } catch (err) {
        console.error("Failed to fetch graph data:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraph();
    const interval = setInterval(fetchGraph, 2000);
    return () => clearInterval(interval);
  }, [alertId]);

  const CATEGORIES = [
    { name: "IP Address", itemStyle: { color: "#33B5E5", shadowBlur: 10, shadowColor: 'rgba(51, 181, 229, 0.5)' } },
    { name: "Normal Account", itemStyle: { color: "#00C853" } },
    { name: "Flagged Account", itemStyle: { color: "#E53935", shadowBlur: 15, shadowColor: 'rgba(229, 57, 53, 0.5)' } },
    { name: "Fraud Ring Member", itemStyle: { color: "#F57F17" } },
  ];

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#202530',
      textStyle: { color: '#F8FAFC', fontFamily: '"DM Sans", sans-serif' },
      borderColor: 'rgba(255,255,255,0.05)',
      formatter: '{b}'
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: graphData.nodes,
        links: graphData.edges,
        categories: CATEGORIES,
        roam: true,
        label: {
          show: true,
          position: 'right',
          color: '#8A95A5',
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: 10
        },
        lineStyle: {
          color: '#8A95A5',
          opacity: 0.3,
          curveness: 0.1
        },
        force: {
          repulsion: 350,
          edgeLength: 90,
          gravity: 0.1
        }
      }
    ]
  };

  return (
    <div className="h-full min-h-[400px] flex flex-col bg-slate-surface rounded-xl border border-white/5 shadow-[0_8px_32px_rgba(0,0,0,0.4)] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] rounded-xl z-20" />
      <div className="p-5 border-b border-white/5 flex justify-between items-center bg-black/20 backdrop-blur-sm relative z-10">
        <h2 className="text-lg font-display tracking-wide font-medium flex items-center gap-2 text-on-surface">
          <Network className="w-5 h-5 text-ghost" /> Fraud Ring Topology
        </h2>
      </div>
      <div className="flex-1 p-4 relative bg-slate-bg/30">
        <ReactECharts 
          option={option} 
          style={{ height: '100%', width: '100%' }}
          opts={{ renderer: 'canvas' }}
        />
      </div>
    </div>
  );
}
