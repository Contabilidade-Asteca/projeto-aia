# Asteca AIA
Aplicação dividida em **backend FastAPI** e **frontend React (Vite)** para conversar com o modelo `openai/gpt-oss-20b` via Groq.

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- Chave de API Groq válida (`GROQ_API_KEY`)

## Configurando o backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export GROQ_API_KEY="sua-chave"  # Windows PowerShell: $Env:GROQ_API_KEY="sua-chave"
uvicorn aia_assistente:app --reload
```

O backend ficará disponível em `http://localhost:8000` com o endpoint `POST /api/chat`.

## Configurando o frontend

```bash
cd frontend
npm install
npm run dev
```

O Vite abrirá a interface em `http://localhost:5173`, utilizando proxy para o backend local.

Para produção, execute `npm run build` e faça o deploy do conteúdo da pasta `frontend/dist` em qualquer serviço estático.

## Fluxo de uso

1. Inicie o backend com o `uvicorn`.
2. Rode o frontend com `npm run dev` ou sirva o build.
3. Informe sua pergunta na interface web e, opcionalmente, forneça outra `API Key Groq` no campo da página.

## Comandos úteis

- Encerrar o ambiente virtual: `deactivate`
- Remover dependências Node: `rm -rf node_modules package-lock.json` (caso deseje reinstalar)
