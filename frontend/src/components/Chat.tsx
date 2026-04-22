import { useEffect, useRef, useState } from 'react';
import { sendMessage } from '../api/chat';
import type { ChatMessage } from '../types';
import '../styles/Chat.css';

interface Props {
  projectId: string;
}

export default function Chat({ projectId }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Clear messages when project changes
  useEffect(() => {
    setMessages([]);
  }, [projectId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend() {
    const content = input.trim();
    if (!content || isLoading) return;

    const userMsg: ChatMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const reply = await sendMessage(projectId, content, [...messages, userMsg]);
      setMessages(prev => [...prev, reply]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Something went wrong. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">Send a message to start collaborating with the AI.</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <span className="chat-role">{msg.role === 'user' ? 'You' : 'AI'}</span>
            <p className="chat-content">{msg.content}</p>
          </div>
        ))}
        {isLoading && (
          <div className="chat-bubble assistant">
            <span className="chat-role">AI</span>
            <p className="chat-content chat-thinking">Thinking…</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-row">
        <textarea
          className="chat-input"
          placeholder="Message the AI… (Enter to send, Shift+Enter for newline)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          disabled={isLoading}
        />
        <button className="chat-send-btn" onClick={handleSend} disabled={isLoading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
