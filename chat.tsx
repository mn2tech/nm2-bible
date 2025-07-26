import { useState } from 'react'

const Chat = () => {
  const [userInput, setUserInput] = useState('')
  const [messages, setMessages] = useState([])

  const sendMessage = async () => {
    if (!userInput.trim()) return

    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userInput })
    })

    const data = await res.json()
    setMessages(prev => [...prev, 
      { role: 'user', content: userInput },
      { role: 'assistant', content: data.reply }
    ])
    setUserInput('')
  }

  return (
    <div className="flex flex-col-reverse h-screen">
      <div className="p-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`p-4 my-2 rounded-lg max-w-xl shadow ${
            msg.role === 'assistant' ? 'bg-green-100 text-gray-900' : 'bg-blue-100 text-gray-900'
          }`}>
            {msg.content}
          </div>
        ))}
      </div>

      <div className="p-4 border-t bg-white flex items-center fixed bottom-0 w-full">
        <input
          className="w-full px-4 py-2 border rounded-lg shadow"
          placeholder="Whisper your reflection..."
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
        />
        <button
          className="ml-2 px-4 py-2 bg-indigo-600 text-white rounded-lg shadow"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default Chat