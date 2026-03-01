import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Bot, Clock } from "lucide-react";
import TypewriterText from "./TypewriterText";

const MessageList = ({ messages, isLoading, isUploading, scrollRef }) => {
  return (
    <div className="flex-1 overflow-y-auto p-6 md:p-12 space-y-8 scrollbar-hide bg-[#F8FAFC]">
      <div className="max-w-4xl mx-auto">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={idx}
              className={`flex mb-8 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex gap-4 max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                {/* Avatar */}
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-white border border-slate-200 text-indigo-600"
                  }`}
                >
                  {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
                </div>

                {/* Bubble */}
                <div
                  className={`rounded-2xl px-6 py-4 shadow-sm text-[15px] leading-relaxed relative ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white rounded-tr-none shadow-indigo-200/50 shadow-lg"
                      : "bg-white border border-slate-200 text-slate-700 rounded-tl-none"
                  }`}
                >
                  {msg.role === "assistant" &&
                  idx === messages.length - 1 &&
                  idx !== 0 ? (
                    <TypewriterText text={msg.content} />
                  ) : (
                    msg.content
                  )}

                  {msg.role === "assistant" && (
                    <div className="mt-4 flex items-center gap-4 border-t border-slate-100 pt-3 text-[11px] text-slate-400 font-medium">
                      <span className="flex items-center gap-1 hover:text-indigo-600 cursor-pointer transition-colors">
                        <Clock size={12} /> Source Check
                      </span>
                      <span className="flex items-center gap-1 hover:text-indigo-600 cursor-pointer transition-colors">
                        Copy response
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading Indicators */}
        {(isLoading || isUploading) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="flex gap-4 items-center bg-white border border-slate-100 rounded-2xl px-6 py-4 shadow-xl shadow-slate-200/50">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce"></span>
              </div>
              <span className="text-sm text-slate-500 font-semibold italic">
                {isUploading ? "Syncing document..." : "Reviewing policies..."}
              </span>
            </div>
          </motion.div>
        )}
        <div ref={scrollRef} className="h-10" />
      </div>
    </div>
  );
};

export default MessageList;
