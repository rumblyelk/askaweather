import { useState, useRef, useEffect } from 'react';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatState = {
  messages: Message[];
  input: string;
  isLoading: boolean;
  error?: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function ChatInterface() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    input: '',
    isLoading: false
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = 'auto';
      textAreaRef.current.style.height = `${Math.min(textAreaRef.current.scrollHeight, 120)}px`;
    }
  }, [state.input]);

  const sendMessage = async () => {
    if (!state.input.trim() || state.isLoading) return;
    
    // Reset height after sending
    if (textAreaRef.current) {
      textAreaRef.current.style.height = 'auto';
    }

    const userMessage: Message = { role: 'user', content: state.input };
    const newMessages = [...state.messages, userMessage];

    setState(prev => ({
      ...prev,
      messages: newMessages,
      input: '',
      isLoading: true,
      error: undefined
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const data = await response.json();
      
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, data.message],
        isLoading: false
      }));

    } catch (err) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to connect to the assistant. Please try again.'
      }));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-gradient-to-br from-sky-200 via-sky-100 to-white p-4 font-sans text-slate-700">
      {/* Main Glassmorphism Card */}
      <div className="flex h-[85vh] w-full max-w-3xl flex-col overflow-hidden rounded-[2rem] border border-white/50 bg-white/60 text-left shadow-2xl backdrop-blur-xl transition-all duration-300">
        
        {/* Header */}
        <div className="border-b border-white/30 bg-white/40 px-8 py-5 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-tr from-sky-400 to-blue-500 text-white shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-6 w-6">
                <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-800">Askaweather</h1>
              <p className="text-xs font-medium text-slate-500">Your Personal Forecast Assistant</p>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 space-y-6 overflow-y-auto px-8 py-6 scrollbar-thin scrollbar-thumb-sky-200 hover:scrollbar-thumb-sky-300">
          {state.messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center text-slate-400">
              <div className="mb-4 rounded-full bg-sky-50 p-6 shadow-inner">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-12 w-12 text-sky-300">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
                </svg>
              </div>
              <p className="text-lg font-medium">How's the weather looking?</p>
              <p className="text-sm">Try asking about your city or upcoming plans.</p>
            </div>
          )}
          
          {state.messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`relative max-w-[85%] rounded-2xl px-5 py-3.5 text-[0.95rem] leading-relaxed shadow-sm transition-all
                  ${msg.role === 'user' 
                    ? 'rounded-tr-sm bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-blue-200' 
                    : 'rounded-tl-sm bg-white text-slate-700 shadow-slate-200'
                  }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          
          {state.isLoading && (
            <div className="flex w-full justify-start">
              <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-white px-5 py-4 shadow-sm shadow-slate-200">
                <div className="h-2 w-2 animate-bounce rounded-full bg-sky-400 [animation-delay:-0.3s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-sky-400 [animation-delay:-0.15s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-sky-400"></div>
              </div>
            </div>
          )}
          
          {state.error && (
            <div className="mx-auto max-w-md rounded-xl bg-red-50 p-3 text-center text-sm text-red-600 shadow-sm ring-1 ring-red-100">
              {state.error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-white/50 bg-white/40 p-6 backdrop-blur-md">
          <div className="relative flex items-end gap-2">
            <textarea
              ref={textAreaRef}
              value={state.input}
              onChange={(e) => setState(prev => ({ ...prev, input: e.target.value }))}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything..."
              disabled={state.isLoading}
              rows={1}
              className="w-full resize-none rounded-3xl border-0 bg-white py-3.5 pl-6 pr-14 text-slate-700 shadow-sm ring-1 ring-slate-200/50 placeholder:text-slate-400 focus:ring-2 focus:ring-sky-400 disabled:opacity-50 min-h-[50px] max-h-[120px]"
            />
            <button
              onClick={sendMessage}
              disabled={state.isLoading || !state.input.trim()}
              className="absolute right-2 bottom-1.5 flex h-10 w-10 items-center justify-center rounded-full bg-blue-500 text-white shadow-md transition-all hover:bg-blue-600 hover:shadow-lg hover:shadow-blue-200 active:scale-95 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5 ml-0.5">
                <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
              </svg>
            </button>
          </div>
        </div>
        
      </div>
      
      {/* Footer */}
      <div className="mt-6 text-xs font-medium text-slate-400/80">
        Powered by Claude & WeatherAPI
      </div>
    </div>
  );
}
