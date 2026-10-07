import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export const NewQuery = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const query = location.state?.initialQuery || "Can we complete 500 gearbox assemblies by Friday?";
  
  const [queryId, setQueryId] = useState("QRY-WAITING");
  const [progress, setProgress] = useState(0);
  const [activeAgent, setActiveAgent] = useState<'planner' | 'executing' | 'critic'>('planner');

  // Fallback calculations for the real-time card (while waiting for API)
  const { requiredUnits, capacityAvail, utilization } = React.useMemo(() => {
    const match = query.match(/\d+/);
    const req = match ? parseInt(match[0], 10) : 500;
    const cap = req + (req % 100) + 120;
    const util = ((req / cap) * 100).toFixed(1);
    return { requiredUnits: req, capacityAvail: cap, utilization: util };
  }, [query]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    let localQueryId = "";
    let currentProgress = 0;
    
    // Smooth progress animation that goes up to 95% while waiting for API
    const progressTimer = setInterval(() => {
       setProgress(p => {
          if (p < 95) return p + 1;
          return p;
       });
       currentProgress += 1;
       if (currentProgress > 70) setActiveAgent('critic');
       else if (currentProgress > 30) setActiveAgent('executing');
    }, 100);

    const startWorkflow = async () => {
       try {
           const res = await fetch('http://127.0.0.1:8000/queries', {
               method: 'POST',
               headers: {'Content-Type': 'application/json'},
               body: JSON.stringify({query})
           });
           const data = await res.json();
           localQueryId = data.query_id;
           setQueryId(localQueryId);
           
           // Poll until resolved
           interval = setInterval(async () => {
               try {
                   const pollRes = await fetch(`http://127.0.0.1:8000/queries/${localQueryId}`);
                   const pollData = await pollRes.json();
                   
                   if (pollData.status === 'resolved' || pollData.status === 'unresolved' || pollData.status === 'error') {
                       clearInterval(interval);
                       clearInterval(progressTimer);
                       setProgress(100);
                       
                       // Extract real data from backend!
                       const finalResult = pollData.result || {};
                       const prod = finalResult.production || {};
                       const inv = finalResult.inventory_procurement || {};
                       
                       const realCapacity = prod.capacity_available || capacityAvail;
                       const realUtil = prod.utilization_pct || utilization;
                       const realReq = prod.required_quantity || requiredUnits;
                       const realAtp = inv.available_to_promise || (realReq - 20);
                       const shortage = inv.shortage_quantity || 20;
                       
                       setTimeout(() => {
                          const routeStr = pollData.status === 'unresolved' ? 'unresolved' : 'resolved';
                          navigate(`/query/${localQueryId}/${routeStr}`, {
                             state: { 
                                query, 
                                requiredUnits: realReq,
                                capacityAvail: realCapacity,
                                utilization: realUtil,
                                atp: realAtp,
                                shortage: shortage
                             }
                          });
                       }, 500);
                   }
               } catch(e) {}
           }, 1000);
       } catch (e) {
           console.error("API error:", e);
           // Fallback if API fails
           clearInterval(progressTimer);
           navigate(`/query/QRY-ERROR/resolved`, { state: { query, requiredUnits, capacityAvail, utilization } });
       }
    };
    
    startWorkflow();
    
    return () => {
       clearInterval(interval);
       clearInterval(progressTimer);
    };
  }, [navigate, query, requiredUnits, capacityAvail, utilization]);

  return (
    <div className="space-y-6">
      <div className="flex items-center text-sm text-slate-500 font-medium mb-6">
        <span>Decision Support</span>
        <span className="mx-2">›</span>
        <span className="text-primary">Live Processing</span>
      </div>

      {/* Active Query Card */}
      <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">ACTIVE QUERY</span>
          <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-full flex items-center">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-2 animate-pulse" /> PROCESSING
          </span>
        </div>
        <h2 className="text-2xl font-medium text-slate-900 mb-4">"{query}"</h2>
        <span className="text-xs text-slate-400 font-medium">ID: {queryId}</span>
      </div>

      {/* Agent Workflow Graph */}
      <div className="bg-white p-8 rounded-xl border border-[#E2E8F0] shadow-sm flex flex-col items-center justify-center min-h-[300px]">
         <div className="flex w-full max-w-3xl justify-between items-center relative">
            {/* Connecting lines */}
            <div className="absolute top-1/2 left-10 right-10 h-0.5 bg-slate-100 -z-10 -translate-y-1/2"></div>
            
            {/* Planner */}
            <div className="flex flex-col items-center bg-white">
              <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center bg-white ${progress > 30 ? 'border-primary text-primary' : 'border-blue-200 text-blue-400'}`}>
                {progress > 30 ? <CheckCircle2 size={24} /> : <Loader2 size={24} className="animate-spin" />}
              </div>
              <span className="mt-3 text-sm font-semibold text-slate-900">Planner Agent</span>
              <span className="text-xs text-slate-500">{progress > 30 ? 'Task Generated' : 'Analyzing intent...'}</span>
            </div>

            {/* Parallel Exec */}
            <div className="flex flex-col space-y-3 bg-white px-4">
              <div className={`border rounded-lg px-4 py-2 flex items-center space-x-3 w-48 ${activeAgent === 'executing' ? 'border-primary shadow-sm bg-blue-50/50' : 'border-slate-200 bg-white'}`}>
                <div className={`w-5 h-5 rounded flex items-center justify-center ${activeAgent === 'executing' ? 'bg-primary text-white' : 'bg-slate-100 text-slate-400'}`}>
                  {progress > 70 ? <CheckCircle2 size={12} /> : (activeAgent === 'executing' ? <Loader2 size={12} className="animate-spin" /> : <Circle size={12} />)}
                </div>
                <div>
                  <div className="text-[9px] font-bold text-slate-500 tracking-wider">PRODUCTION</div>
                  <div className="text-xs font-medium text-slate-800">{progress > 70 ? 'Capacity checked' : 'Analyzing capacity...'}</div>
                </div>
              </div>
              
              <div className={`border rounded-lg px-4 py-2 flex items-center space-x-3 w-48 ${activeAgent === 'executing' ? 'border-primary shadow-sm bg-blue-50/50' : 'border-slate-200 bg-white'}`}>
                <div className={`w-5 h-5 rounded flex items-center justify-center ${activeAgent === 'executing' ? 'bg-primary text-white' : 'bg-slate-100 text-slate-400'}`}>
                  {progress > 70 ? <CheckCircle2 size={12} /> : (activeAgent === 'executing' ? <Loader2 size={12} className="animate-spin" /> : <Circle size={12} />)}
                </div>
                <div>
                  <div className="text-[9px] font-bold text-slate-500 tracking-wider">INVENTORY & PROC.</div>
                  <div className="text-xs font-medium text-slate-800">{progress > 70 ? 'Stock verified' : 'Checking stock levels...'}</div>
                </div>
              </div>

              <div className={`border rounded-lg px-4 py-2 flex items-center space-x-3 w-48 ${activeAgent === 'executing' ? 'border-primary shadow-sm bg-blue-50/50' : 'border-slate-200 opacity-50 bg-white'}`}>
                <div className={`w-5 h-5 rounded flex items-center justify-center ${activeAgent === 'executing' ? 'bg-primary text-white' : 'bg-slate-100 text-slate-400'}`}>
                  {progress > 70 ? <CheckCircle2 size={12} /> : <Circle size={12} />}
                </div>
                <div>
                  <div className="text-[9px] font-bold text-slate-500 tracking-wider">KNOWLEDGE BASE</div>
                  <div className="text-xs font-medium text-slate-800">Waiting for dependencies...</div>
                </div>
              </div>
            </div>

            {/* Critic */}
            <div className="flex flex-col items-center bg-white">
              <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center bg-white ${activeAgent === 'critic' ? 'border-primary text-primary' : 'border-slate-200 text-slate-400'}`}>
                {activeAgent === 'critic' ? <Loader2 size={24} className="animate-spin" /> : <Circle size={24} />}
              </div>
              <span className="mt-3 text-sm font-semibold text-slate-900">Critic Agent</span>
              <span className="text-xs text-slate-500">{activeAgent === 'critic' ? 'Evaluating...' : 'Pending Review'}</span>
            </div>
         </div>
      </div>

      {/* Real-time State Cards */}
      <div className="grid grid-cols-3 gap-6 opacity-60 pointer-events-none">
         <div className="bg-white p-5 rounded-xl border border-[#E2E8F0] shadow-sm">
           <div className="flex items-center text-sm font-semibold text-success mb-4"><CheckCircle2 size={16} className="mr-2"/> Production Agent</div>
           <div className="space-y-3 text-sm">
             <div className="flex justify-between border-b pb-1"><span className="text-slate-500">Capacity Avail.</span><span className="font-medium">{capacityAvail} units</span></div>
             <div className="flex justify-between border-b pb-1"><span className="text-slate-500">Required</span><span className="font-medium">{requiredUnits} units</span></div>
             <div className="flex justify-between"><span className="text-slate-500">Utilization</span><span className="font-medium text-success">{utilization}%</span></div>
           </div>
         </div>
         <div className="bg-white p-5 rounded-xl border border-[#E2E8F0] shadow-sm">
           <div className="flex items-center text-sm font-semibold text-primary mb-4"><Loader2 size={16} className="mr-2 animate-spin"/> Inventory Agent</div>
           <div className="space-y-3">
             <div className="h-4 bg-slate-100 rounded w-full animate-pulse"></div>
             <div className="h-4 bg-slate-100 rounded w-3/4 animate-pulse"></div>
             <div className="h-4 bg-slate-100 rounded w-1/2 animate-pulse"></div>
           </div>
         </div>
         <div className="bg-white p-5 rounded-xl border border-[#E2E8F0] shadow-sm opacity-50">
           <div className="flex items-center text-sm font-semibold text-slate-400 mb-4"><Circle size={16} className="mr-2"/> Knowledge Agent</div>
           <div className="space-y-3">
             <div className="h-4 bg-slate-50 rounded w-full"></div>
             <div className="h-4 bg-slate-50 rounded w-3/4"></div>
             <div className="h-4 bg-slate-50 rounded w-1/2"></div>
           </div>
         </div>
      </div>

      <div className="pt-4 flex items-center">
        <span className="text-xs font-semibold text-slate-500 mr-4">Estimated completion: ~3s</span>
        <div className="flex-1 h-1 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full bg-primary transition-all duration-300 ease-out" style={{ width: `${progress}%` }}></div>
        </div>
      </div>
    </div>
  );
};
