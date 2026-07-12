import os
from dotenv import load_dotenv
load_dotenv()

keys = {
    'GEMINI_API_KEY': bool(os.getenv('GEMINI_API_KEY')),
    'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
    'ANTHROPIC_API_KEY': bool(os.getenv('ANTHROPIC_API_KEY')),
    'GITHUB_TOKEN': bool(os.getenv('GITHUB_TOKEN')),
    'OPENROUTER_API_KEY': bool(os.getenv('OPENROUTER_API_KEY')),
    'GROQ_API_KEY': bool(os.getenv('GROQ_API_KEY')),
    'REPLICATE_API_KEY': bool(os.getenv('REPLICATE_API_KEY')),
}
print("=== API Anahtarlari ===")
for k, v in keys.items():
    print(f"  {k}: {'VAR' if v else 'YOK'}")
