import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { RefreshCw, PanelLeftOpen } from "lucide-react";

// IMPORTANT: Component Imports
import Sidebar from "./components/Sidebar";
import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";

const App = () => {
  // UI States
  const [showSidebar, setShowSidebar] = useState(true);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Data States
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am ready to analyze your HR documents. Please upload a handbook or ask a specific policy question.",
    },
  ]);

  const history = [
    { id: 1, title: "Employee Benefits 2024", date: "2 hours ago" },
    { id: 2, title: "Remote Work Policy", date: "Yesterday" },
    { id: 3, title: "Sick Leave Procedures", date: "Mar 1, 2026" },
  ];

  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, isUploading]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post(
        "http://localhost:8000/upload",
        formData,
      );
      setMessages((p) => [
        ...p,
        {
          role: "assistant",
          content: `✅ Document ingested: ${response.data.message}`,
        },
      ]);
    } catch (err) {
      setMessages((p) => [
        ...p,
        { role: "assistant", content: "❌ Error uploading document." },
      ]);
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input;
    setMessages((p) => [...p, { role: "user", content: userMsg }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/ask", {
        question: userMsg,
      });
      setMessages((p) => [
        ...p,
        { role: "assistant", content: response.data.answer },
      ]);
    } catch (err) {
      setMessages((p) => [
        ...p,
        { role: "assistant", content: "Backend Error: Connection refused." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#F8FAFC] overflow-hidden font-sans">
      {/* Sidebar Component */}
      <Sidebar
        history={history}
        isVisible={showSidebar}
        setIsVisible={setShowSidebar}
      />

      <main className="flex-1 flex flex-col relative">
        {/* Top Navigation */}
        <header className="h-16 bg-white/40 backdrop-blur-md border-b border-slate-100 px-8 flex items-center justify-between z-10">
          <div className="flex items-center gap-4">
            {!showSidebar && (
              <button
                onClick={() => setShowSidebar(true)}
                className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all"
              >
                <PanelLeftOpen size={22} />
              </button>
            )}
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></span>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                System Status: Active
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => window.location.reload()}
              className="p-2 text-slate-400 hover:bg-slate-100 rounded-lg transition-all"
            >
              <RefreshCw size={18} />
            </button>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 border-2 border-white shadow-sm"></div>
          </div>
        </header>

        {/* Message Container Component */}
        <MessageList
          messages={messages}
          isLoading={isLoading}
          isUploading={isUploading}
          scrollRef={scrollRef}
        />

        {/* Input Bar Component */}
        <ChatInput
          input={input}
          setInput={setInput}
          handleSend={handleSend}
          handleFileUpload={handleFileUpload}
          fileInputRef={fileInputRef}
          isLoading={isLoading}
          isUploading={isUploading}
        />
      </main>
    </div>
  );
};

export default App;
