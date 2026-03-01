import React from "react";
import { Paperclip, Send } from "lucide-react";

const ChatInput = ({
  input,
  setInput,
  handleSend,
  handleFileUpload,
  fileInputRef,
  isLoading,
  isUploading,
}) => {
  return (
    <div className="p-8 bg-gradient-to-t from-[#F8FAFC] via-[#F8FAFC] to-transparent">
      <div className="max-w-4xl mx-auto bg-white rounded-3xl p-2 shadow-2xl shadow-indigo-100 border border-slate-200 flex items-center gap-2 group focus-within:ring-2 ring-indigo-500/20 transition-all">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf"
          className="hidden"
        />

        <button
          type="button"
          onClick={() => fileInputRef.current.click()}
          disabled={isUploading}
          className="p-4 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-2xl transition-all"
          title="Upload Handbook"
        >
          <Paperclip size={22} />
        </button>

        <form onSubmit={handleSend} className="flex-1 flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Search company policy..."
            className="flex-1 bg-transparent border-none py-4 text-slate-700 placeholder:text-slate-400 outline-none px-2 font-medium"
          />
          <button
            type="submit"
            disabled={isLoading || isUploading || !input.trim()}
            className="bg-indigo-600 text-white p-4 rounded-2xl hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 transition-all active:scale-95 flex items-center gap-2 shadow-lg shadow-indigo-200"
          >
            <Send size={18} />
            <span className="hidden md:inline font-bold text-sm pr-2">
              Analyze
            </span>
          </button>
        </form>
      </div>
      <p className="text-center text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em] mt-4">
        AI-Powered Policy Verification System
      </p>
    </div>
  );
};

export default ChatInput;
