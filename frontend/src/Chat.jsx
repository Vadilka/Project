import React, { useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError("");

    // Добавляем сообщение пользователя в историю
    const newMessages = [
      ...messages,
      { content: input, role: "user" }
    ];
    setMessages(newMessages);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: input,
          language: "pl"
        }),
      });
      if (!response.ok) throw new Error("Błąd odpowiedzi serwera");
      const data = await response.json();
      setMessages([
        ...newMessages,
        { content: data.response, role: "bot", sources: data.sources }
      ]);
      setInput("");
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Chatbot</h2>
      <div
        style={{
          background: "#222",
          color: "#fff",
          padding: 16,
          borderRadius: 8,
          minHeight: 200,
          marginBottom: 16,
        }}
      >
        {messages.length === 0 && <div>Brak wiadomości. Zadaj pytanie!</div>}
        {messages.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: 12 }}>
            <b>{msg.role === "user" ? "Ty:" : "Bot:"}</b> {msg.content}
            {msg.role === "bot" && msg.sources && (
              <div style={{ fontSize: 12, color: "#aaa" }}>
                Źródła: {msg.sources.filter(Boolean).join(", ")}
              </div>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Zadaj pytanie..."
          style={{ flex: 1, padding: 8 }}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Wyślij
        </button>
      </form>
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
    </div>
  );
}
