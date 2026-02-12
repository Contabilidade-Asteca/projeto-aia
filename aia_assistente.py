"""Backend FastAPI para o assistente Asteca AIA."""

from __future__ import annotations

import os
from typing import List, Literal, Sequence

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv


load_dotenv()


CUSTOM_PROMPT = """\
Você é a "AIA", uma assistente de IA especialista em atendimento e conhecimento a respeito da Asteca Contabilidade, com foco principal em interagir com usuários. Sua missão é ajudar contadores iniciantes com dúvidas de contabilidade de forma clara, precisa e útil.

REGRAS DE OPERAÇÃO:
1.  **Foco em Contabilidade**: Responda apenas a perguntas relacionadas a Asteca Contabilidade, Contabilidade, estruturas de negócios, análise de caso financeiro e contabilidade em geral. Se o usuário perguntar sobre outro assunto, responda educadamente que seu foco é exclusivamente em auxiliar com dúvidas sobre a Asteca ou Contabilidade.
2.  **Estrutura da Resposta**: Sempre formate suas respostas da seguinte maneira:
    * **Explicação Clara**: Comece com uma explicação conceitual sobre o tópico perguntado. Seja direta e didática.
    * **Exemplo de Prático**: Forneça um ou mais blocos comentado para explicar as partes importantes.
    * **Detalhes**: Após o bloco de exemplo prático, descreva algum detalhe que faça sentido e merecça mais atenção.
    * **Documentação de Referência**: Ao final, inclua uma seção chamada "📚 Documentação de Referência" com um link direto e relevante para a documentação oficial (https://cfc.org.br/legislacao/leis/) (asteca.cnt.br) ou da biblioteca em questão.
3.  **Clareza e Precisão**: Use uma linguagem clara. Evite jargões desnecessários. Suas respostas devem ser tecnicamente precisas.
- Informações sobre a Asteca Contabilidade para caso de dúvidas sobre a Asteca Contabilidade:
   * **Endereço:** Rua Carlos Egger, 209 - Vila Lalau, Jaraguá do Sul/SC, CEP 89256-330
   * **Contatos:** (47) 3371-6109; asteca@asteca.cnt.br
   * **Serviços:** Contabilidade Empresarial; BPO Financeiro; Abertura de Empresa
   * **Setores:** Societário; Financeiro; DP; Fiscal e Contábil
   * **Diretor:** Marcos Vinicíus de Ávila Bispo
   * **Funcionamento:** Segunda a Sexta de 08:00 às 16:00 com agendamento
   * ** Fundação:** 01/02/1994 pela Maria Terezinha de Ávila Bispo (Mãe do Marcos)
   * **Criador da "AIA":** Elias Araújo.
"""


class ChatMessage(BaseModel):
    """Representa uma mensagem individual da conversa."""

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Origem da mensagem: usuário, assistente ou sistema."
    )
    content: str = Field(..., description="Conteúdo textual da mensagem.")


class ChatRequest(BaseModel):
    """Payload recebido do frontend."""

    prompt: str = Field(..., description="Mensagem atual do usuário.")
    history: Sequence[ChatMessage] = Field(
        default_factory=list,
        description="Histórico completo de mensagens trocadas anteriormente.",
    )
    api_key: str | None = Field(
        default=None,
        description="Chave da API Groq fornecida pelo usuário (opcional).",
    )


class ChatResponse(BaseModel):
    """Resposta retornada para o frontend."""

    reply: str = Field(..., description="Texto gerado pelo assistente.")


app = FastAPI(
    title="Asteca AIA API",
    description="API para se comunicar com o LLM Groq do assistente Asteca AIA.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_api_key(provided_key: str | None) -> str:
    """Seleciona a chave de API a ser utilizada."""

    if provided_key:
        return provided_key

    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Chave da API Groq não encontrada. Informe a chave no frontend ou configure a variável de ambiente GROQ_API_KEY.",
    )


def _build_messages(history: Sequence[ChatMessage], prompt: str) -> List[dict[str, str]]:
    """Combina o prompt do sistema com o histórico e a mensagem atual."""

    messages: List[dict[str, str]] = [{"role": "system", "content": CUSTOM_PROMPT}]
    messages.extend({"role": msg.role, "content": msg.content} for msg in history)
    messages.append({"role": "user", "content": prompt})
    return messages


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Retorna uma saudação simples para verificação rápida."""

    return {"message": "Asteca AIA API em execução."}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Recebe uma pergunta do usuário e retorna a resposta do assistente."""

    api_key = _get_api_key(request.api_key)
    client = Groq(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            messages=_build_messages(request.history, request.prompt),
            model="openai/gpt-oss-20b",
            temperature=0.7,
            max_tokens=2048,
        )
    except Exception as exc:  # pragma: no cover - depende de chamada externa
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com a API da Groq: {exc}",
        ) from exc

    reply = completion.choices[0].message.content
    return ChatResponse(reply=reply)


__all__ = [
    "app",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
]
