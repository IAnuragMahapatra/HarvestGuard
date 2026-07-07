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
        data: graphData.nodes,
        links: graphData.edges,
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
