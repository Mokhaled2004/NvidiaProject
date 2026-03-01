import React from "react";
import {
  ShieldCheck,
  Plus,
  MessageSquare,
  Settings,
  LogOut,
  PanelLeftClose,
  ChevronRight,
} from "lucide-react";
import { motion } from "framer-motion";

const Sidebar = ({ history, isVisible, setIsVisible }) => {
  if (!isVisible) return null;

  return (
    <motion.aside
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -300, opacity: 0 }}
      className="w-80 h-[calc(100vh-2rem)] m-4 mr-0 bg-white/70 backdrop-blur-xl flex flex-col border border-slate-200 shadow-xl shadow-slate-200/50 rounded-[2.5rem] overflow-hidden transition-all z-20"
    >
      <div className="p-6 h-full flex flex-col">
        {/* Header with Close Button */}
        <div className="flex items-center justify-between mb-8 px-2">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-2xl shadow-lg shadow-indigo-100">
              <ShieldCheck className="text-white" size={22} />
            </div>
            <span className="text-slate-800 font-bold text-lg tracking-tight">
              Guardrail
            </span>
          </div>
          <button
            onClick={() => setIsVisible(false)}
            className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all"
          >
            <PanelLeftClose size={20} />
          </button>
        </div>

        {/* Action Button */}
        <button className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-2xl shadow-lg shadow-indigo-100 transition-all active:scale-95 mb-8 font-semibold text-sm">
          <Plus size={18} strokeWidth={3} />
          New Analysis
        </button>

        {/* History List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4 px-4">
            Recent Inquiries
          </p>
          {history.map((item) => (
            <div
              key={item.id}
              className="group flex items-center justify-between p-4 rounded-2xl hover:bg-indigo-50/50 cursor-pointer transition-all border border-transparent hover:border-indigo-100"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="bg-slate-100 p-2 rounded-lg group-hover:bg-white transition-colors">
                  <MessageSquare
                    size={14}
                    className="text-slate-500 group-hover:text-indigo-600"
                  />
                </div>
                <div className="flex flex-col overflow-hidden">
                  <span className="text-sm font-semibold text-slate-700 truncate group-hover:text-indigo-900">
                    {item.title}
                  </span>
                  <span className="text-[10px] text-slate-400 font-medium italic">
                    {item.date}
                  </span>
                </div>
              </div>
              <ChevronRight
                size={14}
                className="text-slate-300 opacity-0 group-hover:opacity-100 transition-all"
              />
            </div>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="mt-6 pt-6 border-t border-slate-100 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all font-medium text-sm">
            <Settings size={18} />
            Settings
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-rose-500 hover:bg-rose-50 rounded-xl transition-all font-medium text-sm">
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
