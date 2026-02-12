import os
from typing import Literal, Sequence

from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

CUSTOM_PROMPT = """Você é a "AIA", uma assistente de IA especialista em atendimento e conhecimento a respeito da Asteca Contabilidade, com foco principal em interagir com usuários. Sua missão é ajudar contadores iniciantes com dúvidas de contabilidade de forma clara, precisa e útil.

REGRAS DE OPERAÇÃO:
1. **Foco em Contabilidade**: Responda apenas a perguntas relacionadas a Contabilidade, estruturas de negócios, análise de caso financeiro e contabilidade em geral. Se o usuário perguntar sobre outro assunto, responda educadamente que seu foco é exclusivamente em auxiliar com dúvidas sobre a Asteca ou Contabilidade.

2. **Estrutura da Resposta**: Sempre formate suas respostas seguindo a estrutura abaixo **em Markdown**:
   - Use títulos e subtítulos com #, ##, ###.
   - Use **negrito**, listas com -, e blocos de código com ``` quando fizer sentido.
   - Se precisar de tabela, use **tabela Markdown** (não ASCII).

   Estrutura obrigatória:
   ## Explicação Clara
   (explicação conceitual, direta e didática)

   ## Exemplo Prático
   (um ou mais exemplos em bloco de código Markdown)

   ## Detalhes
   (pontos de atenção e observações úteis)

   ## 📚 Documentação de Referência
   (links diretos e relevantes: https://cfc.org.br/legislacao/leis/ e/ou asteca.cnt.br e/ou documentação da biblioteca mencionada)

3. **Clareza e Precisão**: Use uma linguagem clara. Evite jargões desnecessários. Suas respostas devem ser tecnicamente precisas.

4. Informações sobre a Asteca Contabilidade para caso de dúvidas sobre a Asteca Contabilidade:
   - **Endereço:** Rua Carlos Egger, 209 - Vila Lalau, Jaraguá do Sul, Santa Catarina, CEP 89256-330
   - **Contatos:** (47) 3371-6109; asteca@asteca.cnt.br
   - **Serviços:** Contabilidade Empresarial; BPO Financeiro; Abertura de Empresa
   - **Setores:** Societário; Financeiro; DP; Fiscal e Contábil
   - **Diretor:** Marcos Vinicíus de Ávila Bispo
   - **Funcionamento:** Segunda a Sexta de 08:00 às 16:00 com agendamento
   - **Fundação:** 01/02/1994 pela Maria Terezinha de Ávila Bispo (Mãe do Marcos)
   - **Criador da "AIA":** Elias Araújo.

Este é apenas um modelo, seja simpática e humanizada com os usuários, não precisa seguir esses passos a risca todas as vezes.
"""

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    prompt: str
    history: Sequence[ChatMessage] = []
    api_key: str | None = None

class ChatResponse(BaseModel):
    reply: str

app = FastAPI()

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COOKIE_NAME = "groq_api_key"

@app.post("/api/set-key")
def set_key(request: Request, response: Response):
    body = request.json()
    api_key = body.get("apiKey", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key vazia.")
    response.set_cookie(
        key=COOKIE_NAME,
        value=api_key,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=30 * 24 * 60 * 60,
        path="/",
    )
    return {"ok": True}

@app.post("/api/clear-key")
def clear_key(response: Response):
    response.delete_cookie(key=COOKIE_NAME)
    return {"ok": True}

def _get_api_key(request: Request, provided_key: str | None):
    if provided_key:
        return provided_key
    api_key = request.cookies.get(COOKIE_NAME)
    if api_key:
        return api_key
    raise HTTPException(status_code=400, detail="Chave da API não encontrada.")

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest):
    api_key = _get_api_key(request, payload.api_key)

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        messages=[{"role": "system", "content": CUSTOM_PROMPT}]
        + [{"role": m.role, "content": m.content} for m in payload.history]
        + [{"role": "user", "content": payload.prompt}],
        model="openai/gpt-oss-20b",
    )
    reply = completion.choices[0].message.content
    return ChatResponse(reply=reply)
