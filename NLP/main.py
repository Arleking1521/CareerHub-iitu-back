"""FastAPI service wrapping the resume summary generation pipeline."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import Groq
from pydantic import BaseModel, Field

# Load environment variables from project root .env if present
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)

app = FastAPI(title="Resume Summary Generator")

MODEL = "openai/gpt-oss-120b"

BASE_DIR = Path(__file__).parent
PROMPT_PATH = BASE_DIR / "prompts" / "summary.txt"


class Project(BaseModel):
    name: str
    description: str


class CandidateData(BaseModel):
    education_year: str = Field(..., alias="educationYear")
    specialization: str
    target_role: str = Field(..., alias="targetRole")
    skills: list[str]
    projects: list[Project]
    personal_traits: list[str] = Field(..., alias="personalTraits")
    language: str = "ru"

    class Config:
        populate_by_name = True


class SummaryResponse(BaseModel):
    field: str = "summary"
    text: str


def read_text(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Text file not found: {path}") from e


def generate_text(prompt_template: str, input_data: dict) -> str:
    api_key = os.getenv("GROQ_API") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Environment variable GROQ_API or GROQ_API_KEY is not set")

    client = Groq(api_key=api_key)

    user_prompt = f"Данные пользователя:\n{json.dumps(input_data, ensure_ascii=False, indent=2)}"
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"{prompt_template.strip()}"},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content
        if not text or not text.strip():
            raise ValueError("LLM returned empty text")
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Groq API call failed: {e}") from e


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate-summary", response_model=SummaryResponse)
async def generate_summary(data: CandidateData) -> SummaryResponse:
    if not PROMPT_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Prompt file not found: {PROMPT_PATH}")

    prompt_template = read_text(PROMPT_PATH)

    try:
        generated_text = generate_text(prompt_template, data.model_dump(by_alias=True))
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return SummaryResponse(text=generated_text)
