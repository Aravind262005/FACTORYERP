import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, ArrowRight } from 'lucide-react';

export const Dashboard = () => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleAnalyze = () => {
    if (!query.trim()) return;
    // Real implementation would POST to /queries here
    // We will navigate to the live processing page with a mock query ID
    navigate('/query/new', { state: { initialQuery: query } });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Dashboard</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { title: "QUERIES TODAY", value: "42", metric: "+12%", color: "text-success" },
          { title: "AVG RESPONSE TIME", value: "6.2s", metric: "", color: "" },
          { title: "DECISIONS RESOLVED", value: "94%", metric: "", color: "" },
          { title: "PENDING REVIEW", value: "3", metric: "●", color: "text-warning" }
        ].map((stat, i) => (
          <div key={i} className="bg-white p-5 rounded-xl border border-[#E2E8F0] shadow-sm flex flex-col justify-between h-28">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{stat.title}</span>
            <div className="flex items-end justify-between">
              <span className="text-3xl font-bold text-slate-900">{stat.value}</span>
              {stat.metric && (
                <span className={`text-sm font-semibold ${stat.color}`}>{stat.metric}</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Query Input */}
        <div className="col-span-2 bg-white rounded-xl border border-[#E2E8F0] shadow-sm flex flex-col h-[400px]">
          <div className="p-6 flex-1 flex flex-col">
            <h3 className="text-sm font-medium text-slate-700 mb-4">Ask a Manufacturing Question</h3>
            <textarea 
              className="flex-1 w-full bg-slate-50 border border-slate-200 rounded-lg p-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none"
              placeholder="e.g. Can we complete 500 gearbox assemblies by Friday considering current inventory and machine maintenance schedules?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
            <button className="p-2 text-slate-400 hover:text-primary transition-colors rounded-full hover:bg-slate-50">
              <Mic size={20} />
            </button>
            <button 
              onClick={handleAnalyze}
              className="bg-primary hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg text-sm font-medium flex items-center transition-colors"
            >
              Analyze <ArrowRight size={16} className="ml-2" />
            </button>
          </div>
        </div>

        {/* Recent Decisions */}
        <div className="col-span-1 bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-700">Recent Decisions</h3>
            <button className="text-xs text-primary font-medium hover:underline">View All</button>
          </div>
          <div className="space-y-4 overflow-auto flex-1 pr-2">
            {[
              {
                title: '"Are there alternative suppliers for Aluminum Alloy 6061 immediately?"',
                status: 'RESOLVED',
                statusColor: 'bg-green-100 text-green-700',
                match: '98%',
                time: '2h ago'
              },
              {
                title: '"Impact of rescheduling Line B maintenance to next Tuesday?"',
                status: 'NEEDS REVIEW',
                statusColor: 'bg-amber-100 text-amber-700',
                match: '85%',
                time: '4h ago'
              },
              {
                title: '"Query QRY-2023-0879"',
                status: 'RESOLVED',
                statusColor: 'bg-green-100 text-green-700',
                match: '99%',
                time: '1d ago'
              }
            ].map((d, i) => (
              <div key={i} className="p-4 border border-slate-100 rounded-lg hover:border-slate-300 transition-colors cursor-pointer group">
                <p className="text-sm text-slate-800 font-medium leading-snug group-hover:text-primary transition-colors">{d.title}</p>
                <div className="flex items-center justify-between mt-3">
                  <div className="flex items-center space-x-3">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${d.statusColor}`}>{d.status}</span>
                    <span className="text-[11px] text-slate-500 font-medium">{d.match} Match</span>
                  </div>
                  <span className="text-[11px] text-slate-400">{d.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
