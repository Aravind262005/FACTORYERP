import React from 'react';
import { ChevronRight, AlertTriangle, AlertCircle, Factory, Package, BookOpen, RefreshCw, ArrowRight } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';

export const DecisionUnresolved = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center text-sm text-slate-500 font-medium mb-6">
        <span className="hover:text-primary cursor-pointer" onClick={() => navigate('/history')}>Query History</span>
        <ChevronRight size={16} className="mx-1" />
        <span className="text-slate-900">{id || 'QRY-2023-0891'}</span>
      </div>

      {/* Top Banner */}
      <div className="bg-white rounded-xl border border-red-200 shadow-sm overflow-hidden">
        <div className="p-6 flex items-start space-x-6">
          <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0">
            <AlertTriangle size={24} className="text-error" />
          </div>
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-2 py-0.5 bg-red-50 text-error text-[10px] font-bold rounded uppercase tracking-wider">Unresolved</span>
              <h2 className="text-xl font-bold text-slate-900">Unable to Establish a Reliable Decision</h2>
            </div>
            <p className="text-sm text-slate-600">Autonomous decision engine could not reach consensus for Order #8821. Human intervention required.</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Context */}
        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
          <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">QUERY CONTEXT</h3>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between items-start">
              <span className="text-slate-500 w-1/3">Source Request</span>
              <span className="font-medium text-slate-900 text-right">Schedule emergency production run for client AlphaCorp.</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Target Deadline</span>
              <span className="font-medium text-slate-900">Oct 22, 2023 - 17:00</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Priority Level</span>
              <span className="text-error font-medium flex items-center"><AlertCircle size={14} className="mr-1" /> High</span>
            </div>
          </div>
        </div>

        {/* Constraint Log */}
        <div className="bg-red-50 rounded-xl border border-red-100 shadow-sm p-6">
          <h3 className="text-[10px] font-bold text-error uppercase tracking-wider mb-4 border-b border-red-100 pb-2 flex items-center">
            <AlertCircle size={14} className="mr-2" /> CONSTRAINT VIOLATION LOG
          </h3>
          <div className="space-y-4 text-sm text-red-900">
            <p>Inventory Agent and Production Agent outputs conflict after 2 retry attempts.</p>
            <p className="font-semibold text-error">Constraint Violation: Required material (Aluminum Alloy 6061-T6) exceeds ATP (Available-to-Promise) stock for target completion date.</p>
          </div>
        </div>
      </div>

      {/* Agent Comparison */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-6">AGENT OUTPUT COMPARISON</h3>
        <div className="grid grid-cols-3 gap-6">
          {/* Inventory Agent (Failed) */}
          <div className="border border-red-200 rounded-lg p-5 relative bg-white">
            <div className="absolute top-0 right-0 bg-error text-white text-[9px] font-bold px-2 py-1 rounded-bl-lg rounded-tr-lg">CONSTRAINT FAILURE</div>
            <div className="flex items-center mb-6">
              <div className="w-8 h-8 rounded bg-red-50 text-error flex items-center justify-center mr-3">
                <Package size={16} />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900">Inventory Agent</div>
                <div className="text-[9px] text-slate-500 font-medium">NODE: WH-02-AL</div>
              </div>
            </div>
            <div className="space-y-3 text-sm bg-red-50 p-3 rounded-lg border border-red-100">
              <div className="flex justify-between"><span className="text-red-700">Requested</span><span className="font-medium text-slate-900">450 units</span></div>
              <div className="flex justify-between font-bold text-error"><span className="">ATP Stock</span><span className="">210 units</span></div>
              <div className="flex justify-between"><span className="text-red-700">Next Delivery</span><span className="font-medium text-error">Oct 24 (Too late)</span></div>
            </div>
          </div>

          {/* Production Agent (Waiting) */}
          <div className="border border-slate-200 rounded-lg p-5 relative bg-white">
            <div className="absolute top-0 right-0 bg-slate-100 text-slate-500 text-[9px] font-bold px-2 py-1 rounded-bl-lg rounded-tr-lg">AWAITING INPUT</div>
            <div className="flex items-center mb-6">
              <div className="w-8 h-8 rounded bg-slate-50 text-slate-500 flex items-center justify-center mr-3">
                <Factory size={16} />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900">Production Agent</div>
                <div className="text-[9px] text-slate-500 font-medium">NODE: PRO-LINE-B</div>
              </div>
            </div>
            <div className="space-y-3 text-sm p-3">
              <div className="flex justify-between"><span className="text-slate-500">Line Auth</span><span className="font-medium text-slate-900">Line B Approved</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Setup Time</span><span className="font-medium text-slate-900">4.5 Hours</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Dependency</span><span className="font-medium text-slate-400">Awaiting Materials</span></div>
            </div>
          </div>

          {/* Knowledge Agent (Neutral) */}
          <div className="border border-slate-100 rounded-lg p-5 relative bg-slate-50 opacity-60">
            <div className="absolute top-0 right-0 bg-slate-200 text-slate-500 text-[9px] font-bold px-2 py-1 rounded-bl-lg rounded-tr-lg">NOT INVOLVED</div>
            <div className="flex items-center mb-6">
              <div className="w-8 h-8 rounded bg-white text-slate-400 flex items-center justify-center mr-3 border border-slate-200">
                <BookOpen size={16} />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-500">Knowledge Agent</div>
                <div className="text-[9px] text-slate-400 font-medium">NODE: KB-CORE</div>
              </div>
            </div>
            <div className="flex items-center justify-center h-24 text-sm text-slate-400 italic text-center px-4">
              "No conflict detected — not required for this decision path."
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end space-x-4 pt-4">
        <button className="px-4 py-2 bg-white border border-[#E2E8F0] rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 flex items-center">
          <RefreshCw size={14} className="mr-2" /> Retry Analysis
        </button>
        <button className="px-6 py-2 bg-primary hover:bg-blue-700 rounded-lg text-sm font-medium text-white flex items-center">
          Send for Manual Review <ArrowRight size={16} className="ml-2" />
        </button>
      </div>
    </div>
  );
};
