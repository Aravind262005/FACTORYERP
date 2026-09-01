import React from 'react';
import { CheckCircle2, ChevronRight, FileText, Factory, Package, Truck, Lightbulb, BookOpen, ExternalLink, ArrowRight } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';

export const DecisionResolved = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center text-sm text-slate-500 font-medium mb-6">
        <span className="hover:text-primary cursor-pointer" onClick={() => navigate('/history')}>Query History</span>
        <ChevronRight size={16} className="mx-1" />
        <span className="text-slate-900">{id || 'QRY-2023-0904'}</span>
      </div>

      {/* Top Banner */}
      <div className="bg-white rounded-xl border border-green-200 shadow-sm overflow-hidden">
        <div className="h-2 bg-success w-full"></div>
        <div className="p-6 flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">RECOMMENDATION</span>
              <span className="px-2 py-0.5 bg-green-50 text-success text-[10px] font-bold rounded">Resolved</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Production Can Be Completed</h2>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-14 h-14 rounded-full border-4 border-success flex items-center justify-center text-success font-bold text-lg">
              96%
            </div>
          </div>
        </div>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5">
          <div className="flex items-center text-sm font-semibold text-slate-800 mb-6">
            <Factory size={18} className="mr-2 text-slate-400" /> Production
          </div>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">Capacity:</span><span className="font-medium text-slate-900">620 units</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Utilization:</span><span className="font-medium text-slate-900">82.4%</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Wastage:</span><span className="font-medium text-slate-900">3.5%</span></div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-amber-200 shadow-sm p-5 relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-amber-100 text-amber-700 text-[9px] font-bold px-2 py-1 rounded-bl-lg">Action Needed</div>
          <div className="flex items-center text-sm font-semibold text-slate-800 mb-6">
            <Package size={18} className="mr-2 text-slate-400" /> Inventory
          </div>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">ATP (Available-to-Promise):</span><span className="font-medium text-slate-900">480 units</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Shortage:</span><span className="font-bold text-error">-20 units</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Reorder:</span><span className="font-medium text-slate-900">Yes — 150 units (EOQ)</span></div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5">
          <div className="flex items-center text-sm font-semibold text-slate-800 mb-6">
            <BookOpen size={18} className="mr-2 text-slate-400" /> Knowledge Context
          </div>
          <div className="border border-slate-100 bg-slate-50 rounded-lg p-3 flex items-center justify-between group cursor-pointer hover:border-primary/30 transition-colors">
            <div className="flex items-center text-sm text-slate-700">
              <FileText size={16} className="mr-2 text-slate-400 group-hover:text-primary" />
              SOP-14: Expedited Ship...
            </div>
            <ExternalLink size={14} className="text-slate-400" />
          </div>
        </div>
      </div>

      {/* Reasoning */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
        <div className="flex items-center text-sm font-semibold text-slate-800 mb-4">
          <Lightbulb size={18} className="mr-2 text-primary" /> REASONING
        </div>
        <p className="text-sm text-slate-700 leading-relaxed">
          Analysis indicates that while current production line capacity is sufficient to handle the raw manufacturing load, there is a projected 20-unit shortage against the Available-to-Promise (ATP) inventory levels required to fulfill pending commitments.
        </p>
        <p className="text-sm text-slate-700 leading-relaxed mt-4">
          To mitigate this shortfall without disrupting the scheduled production flow, we recommend initiating a 150-unit Economic Order Quantity (EOQ) reorder from Supplier B. This action aligns with the guidelines outlined in SOP-14 for managing expedited inventory constraints while maintaining cost efficiency.
        </p>
      </div>

      {/* Evidence and Actions */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
          <h3 className="text-sm font-semibold text-slate-800 mb-4 border-b border-slate-100 pb-3">Supporting Evidence</h3>
          <ul className="space-y-4">
            <li className="flex items-start">
              <Factory size={16} className="mr-3 text-slate-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-slate-800">Production Schedule</p>
                <p className="text-xs text-slate-500 mt-1">Line 3 & 4 utilization metrics.</p>
              </div>
            </li>
            <li className="flex items-start">
              <Package size={16} className="mr-3 text-slate-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-slate-800">Inventory Record</p>
                <p className="text-xs text-slate-500 mt-1">Current stock and pending allocations.</p>
              </div>
            </li>
            <li className="flex items-start">
              <Truck size={16} className="mr-3 text-slate-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-slate-800">Supplier Data (Supplier B)</p>
                <p className="text-xs text-slate-500 mt-1">Lead times and EOQ constraints.</p>
              </div>
            </li>
            <li className="flex items-start">
              <FileText size={16} className="mr-3 text-slate-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-slate-800">SOP Document</p>
                <p className="text-xs text-slate-500 mt-1">SOP-14 Expedited Shipping Protocols.</p>
              </div>
            </li>
          </ul>
        </div>
        
        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
          <h3 className="text-sm font-semibold text-slate-800 mb-4 border-b border-slate-100 pb-3">Suggested Actions</h3>
          <ul className="space-y-4">
            <li className="flex items-start">
              <input type="checkbox" className="mt-1 mr-3 rounded border-slate-300 text-primary focus:ring-primary" />
              <div>
                <p className="text-sm font-medium text-slate-800">Reorder 150 units from Supplier B</p>
                <p className="text-xs text-slate-500 mt-1">Initiates EOQ purchase order immediately.</p>
              </div>
            </li>
            <li className="flex items-start">
              <input type="checkbox" className="mt-1 mr-3 rounded border-slate-300 text-primary focus:ring-primary" />
              <div>
                <p className="text-sm font-medium text-slate-800">Confirm production schedule</p>
                <p className="text-xs text-slate-500 mt-1">Locks in current capacity allocation for Lines 3 & 4.</p>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div className="flex items-center justify-end space-x-4 pt-4">
        <button className="px-4 py-2 bg-white border border-[#E2E8F0] rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50">Export as PDF</button>
        <button className="px-4 py-2 bg-white border border-[#E2E8F0] rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50">View Full Audit Trail</button>
        <button className="px-6 py-2 bg-primary hover:bg-blue-700 rounded-lg text-sm font-medium text-white flex items-center">
          Approve & Proceed <ArrowRight size={16} className="ml-2" />
        </button>
      </div>
    </div>
  );
};
