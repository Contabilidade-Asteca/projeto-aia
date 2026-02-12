import { useMemo, useState } from 'react'
import './App.css'

const initialAssistantMessage = {
  role: 'assistant',
  content:
    'Olá! Eu sou a AIA, sua assistente virtual da Asteca. Como posso te ajudar hoje?'
}

function App() {
  const [messages, setMessages] = useState([initialAssistantMessage])
  const [input, setInput] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const historyForRequest = useMemo(
    () =>
      messages
        .filter((message) => message !== initialAssistantMessage)
        .map(({ role, content }) => ({ role, content })),
    [messages]
  )

  async function handleSubmit(event) {
    event.preventDefault()
    if (!input.trim() || loading) {
      return
    }

    const prompt = input.trim()
    const userMessage = { role: 'user', content: prompt }
    const updatedMessages = [...messages, userMessage]

    setMessages(updatedMessages)
    setInput('')
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          history: historyForRequest,
          api_key: apiKey || undefined
        })
      })

      if (!response.ok) {
        const { detail } = await response.json().catch(() => ({ detail: 'Erro desconhecido.' }))
        throw new Error(typeof detail === 'string' ? detail : 'Erro inesperado ao consultar o assistente.')
      }

      const data = await response.json()
      setMessages([...updatedMessages, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setError(err.message || 'Não foi possível obter a resposta. Tente novamente.')
      setMessages(updatedMessages)
    } finally {
      setLoading(false)
    }
  }

  function handleClearConversation() {
    setMessages([initialAssistantMessage])
    setError('')
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Asteca AIA</h1>
        <p>Assistente virtual da Asteca Contabilidade</p>
      </header>

      <main className="app__main">
        <section className="panel">
          <div className="panel__header">
            <h2>Conversa</h2>
            <button type="button" className="link-button" onClick={handleClearConversation}>
              Limpar histórico
            </button>
          </div>

          <div className="messages" role="log" aria-live="polite">
            {messages.map((message, index) => (
              <div key={`message-${index}`} className={`message message--${message.role}`}>
                <span className="message__role">{message.role === 'user' ? 'Você' : 'Asteca'}</span>
                <p className="message__content">{message.content}</p>
              </div>
            ))}
          </div>

          {error && <div className="alert alert--error">{error}</div>}

          <form className="chat-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Sua pergunta</span>
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Descreva sua dúvida sobre contabilidade"
                rows={4}
                required
              />
            </label>

            <div className="form-actions">
              <label className="field field--inline">
                <span>API Key Groq (opcional)</span>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(event) => setApiKey(event.target.value)}
                  placeholder="gsk_..."
                />
              </label>

              <button type="submit" className="primary-button" disabled={loading}>
                {loading ? 'Consultando...' : 'Enviar pergunta'}
              </button>
            </div>
          </form>
        </section>

        <aside className="sidebar">
          <h2>Como funciona?</h2>
          <p>
            A AIA se conecta ao modelo <strong>openai/gpt-oss-20b</strong> da Groq para oferecer respostas detalhadas
            sobre Contabilidade e sobre a Asteca. Informe sua dúvida, adicione sua chave Groq (caso queira usar outra) e aguarde a
            resposta estruturada com explicações, exemplos e referências.
          </p>
          <p className="tip">
            Configure a variável <code>GROQ_API_KEY</code> no backend para evitar digitar a chave em cada acesso.
          </p>
        </aside>
      </main>

      <footer className="app__footer">
        <small>Asteca AIA — Desenvolvida para auxiliar na Asteca Contabilidade - Elias Araújo.</small>
      </footer>
    </div>
  )
}

export default App
