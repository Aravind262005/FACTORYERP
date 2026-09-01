import React from 'react';
import { Search, Filter, Eye, ChevronLeft, ChevronRight, AlertTriangle, Cpu, Database } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const QueryHistory = () => {
  const navigate = useNavigate();

  const queries = [
    {
      id: "QRY-2023-0904",
      title: "Analyze yield drop in Line A",
      subtitle: "Correlation found between temperature v...",
      date: "Oct 24, 2023",
      time: "14:32:01",
      status: "Resolved",
      confidence: 94,
      agents: ["AI", "DB"]
    },
    {
      id: "QRY-2023-0891",
      title: "Supply chain delay impact on Q4",
      subtitle: "Insufficient data from tier-2 suppliers.",
      date: "Oct 23, 2023",
      time: "09:15:44",
      status: "Unresolved",
      confidence: 42,
      agents: ["AI"],
      alert: true
    },
    {
      id: "QRY-2023-0879",
      title: "Routine automated diagnostic scan compl...",
      subtitle: "",
      date: "Oct 22, 2023",
      time: "23:00:00",
      status: "Resolved",
      confidence: 99,
      agents: ["SYS"]
    },
    {
      id: "QRY-2023-0878",
      title: "Gearbox assembly inventory check",
      subtitle: "Cross-referencing SAP records with ware...",
      date: "Oct 22, 2023",
      time: "10:05:12",
      status: "Pending",
      confidence: null,
      agents: ["AI", "ER", "IoT"]
    }
  ];

  const handleView = (q: any) => {
    if (q.status === 'Resolved') navigate(`/query/${q.id}/resolved`);
    else if (q.status === 'Unresolved') navigate(`/query/${q.id}/unresolved`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Query History</h2>
        <p className="text-sm text-slate-500">Review and manage past manufacturing intelligence queries.</p>
      </div>

      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden flex flex-col">
        {/* Toolbar */}
        <div className="p-4 border-b border-[#E2E8F0] flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-3 flex-1">
            <select className="bg-white border border-slate-300 text-slate-700 text-sm rounded-md focus:ring-primary focus:border-primary block px-3 py-2">
              <option>Status: All</option>
              <option>Resolved</option>
              <option>Unresolved</option>
              <option>Pending</option>
            </select>
            <div className="flex items-center space-x-2">
              <button className="bg-white border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-md hover:bg-slate-50 flex items-center">
                <span className="mr-2">📅</span> Last 30 Days
              </button>
            </div>
          </div>
          <div className="flex items-center space-x-3">
             <button className="bg-white border border-slate-300 text-slate-700 text-sm font-medium px-4 py-2 rounded-md hover:bg-slate-50 flex items-center">
                <Filter size={16} className="mr-2" /> More Filters
             </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-[10px] uppercase font-bold text-slate-500 tracking-wider border-b border-[#E2E8F0]">
              <tr>
                <th className="px-6 py-4">QUERY DETAILS</th>
                <th className="px-6 py-4">DATE & TIME</th>
                <th className="px-6 py-4">STATUS</th>
                <th className="px-6 py-4">CONFIDENCE</th>
                <th className="px-6 py-4">AGENTS</th>
                <th className="px-6 py-4 text-center">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {queries.map((q, i) => (
                <tr key={i} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-start">
                      {q.alert && <AlertTriangle size={16} className="text-error mr-2 mt-0.5 flex-shrink-0" />}
                      <div>
                        <div className="font-semibold text-slate-900">{q.title}</div>
                        {q.subtitle ? <div className="text-xs text-slate-500 mt-1">{q.subtitle}</div> : <div className="text-xs text-slate-500 mt-1">{q.id}</div>}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-slate-900 font-medium">{q.date}</div>
                    <div className="text-xs text-slate-500 mt-1">{q.time}</div>
                  </td>
                  <td className="px-6 py-4">
                    {q.status === 'Resolved' && <span className="px-2.5 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded-full">Resolved</span>}
                    {q.status === 'Unresolved' && <span className="px-2.5 py-1 bg-red-100 text-red-700 text-[10px] font-bold rounded-full">Unresolved</span>}
                    {q.status === 'Pending' && <span className="px-2.5 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-full">Pending</span>}
                  </td>
                  <td className="px-6 py-4">
                    {q.confidence !== null ? (
                      <div className="flex items-center w-24">
                        <span className={`w-8 font-medium ${q.confidence > 80 ? 'text-success' : 'text-error'}`}>{q.confidence}%</span>
                        <div className="flex-1 h-1.5 bg-slate-100 rounded-full ml-2">
                          <div className={`h-full rounded-full ${q.confidence > 80 ? 'bg-success' : 'bg-error'}`} style={{ width: `${q.confidence}%` }}></div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center w-24">
                        <span className="w-8 font-medium text-slate-400">--%</span>
                        <div className="flex-1 h-1.5 bg-slate-100 rounded-full ml-2">
                          <div className="h-full rounded-full bg-amber-400 w-1/3 animate-pulse"></div>
                        </div>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex space-x-1">
                      {q.agents.map((a, j) => (
                        <div key={j} className="w-6 h-6 rounded bg-blue-50 text-primary flex items-center justify-center text-[9px] font-bold border border-blue-100" title={a}>
                          {a}
                        </div>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button onClick={() => handleView(q)} className="p-1.5 text-slate-400 hover:text-primary hover:bg-blue-50 rounded transition-colors">
                      <Eye size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-[#E2E8F0] flex items-center justify-between bg-slate-50 text-sm text-slate-500">
          <div>Showing 1 to 4 of 128 queries</div>
          <div className="flex items-center space-x-1">
            <button className="px-3 py-1 text-slate-400 cursor-not-allowed">Previous</button>
            <button className="w-8 h-8 flex items-center justify-center bg-primary text-white font-medium rounded">1</button>
            <button className="w-8 h-8 flex items-center justify-center hover:bg-slate-200 text-slate-700 font-medium rounded transition-colors">2</button>
            <button className="w-8 h-8 flex items-center justify-center hover:bg-slate-200 text-slate-700 font-medium rounded transition-colors">3</button>
            <span className="px-2">...</span>
            <button className="w-8 h-8 flex items-center justify-center hover:bg-slate-200 text-slate-700 font-medium rounded transition-colors">32</button>
            <button className="px-3 py-1 text-slate-700 hover:text-primary font-medium transition-colors">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};
