import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import UploadDocument from "./UploadDocument";
import Chat from "./Chat";

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      <h1>Chatbot LLM + RAG dla programu studiów</h1>
      <UploadDocument />
      <Chat />
    </div>
  )
}

export default App
