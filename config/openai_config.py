import os
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI

# Cargar .env de forma robusta (independiente del cwd)
load_dotenv(find_dotenv(), override=True)

def _clean(x: Optional[str]) -> str:
    """Limpia comentarios inline y comillas accidentales en variables .env."""
    if not x:
        return ""
    x = x.split("#", 1)[0].strip()
    if x.startswith(("'", '"')) and x.endswith(("'", '"')):
        x = x[1:-1].strip()
    return x

# Lee variables
_AZ_ENDPOINT  = os.getenv("AZURE_OPENAI_ENDPOINT")
_AZ_API_KEY   = os.getenv("AZURE_OPENAI_API_KEY")
_AZ_API_VER   = os.getenv("AZURE_OPENAI_API_VERSION") or "2024-02-15-preview"
_AZ_DEPLOY    = os.getenv("AZURE_OPENAI_MODEL")

# Cliente
_client = AzureOpenAI(
    azure_endpoint=_AZ_ENDPOINT,
    api_key=_AZ_API_KEY,
    api_version=_AZ_API_VER,
)

def openai_response(
    Role_system: str,
    Prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.2,
    top_p: float = 0.95,
) -> str:
    """
    Llamado básico a Azure OpenAI (chat.completions), leyendo credenciales/endpoint del .env.
    - 'model' por defecto usa AZURE_OPENAI_MODEL (deployment name).
    """
    try:
        mdl = model or _AZ_DEPLOY
        if not (mdl and _AZ_ENDPOINT and _AZ_API_KEY):
            return "[Error OpenAI] Faltan variables en .env (AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY / AZURE_OPENAI_MODEL)."

        messages = [
            {"role": "system", "content": Role_system},
            {"role": "user",   "content": Prompt},
        ]

        completion = _client.chat.completions.create(
            model=mdl,  # deployment name
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        # Devuelve info útil sin exponer la key
        return f"[Error OpenAI] endpoint={_AZ_ENDPOINT} | version={_AZ_API_VER} | model={model or _AZ_DEPLOY} | {e}"
    

    