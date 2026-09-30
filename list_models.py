from google import genai

with open(r"c:\Users\cedbo\OneDrive\Documents\pedo\.env", "r") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

client = genai.Client(api_key=api_key)

try:
    models = list(client.models.list())
    print(f"Total models available: {len(models)}")
    for m in models:
        if "gemini" in m.name.lower():
            print(f"- {m.name}")
except Exception as e:
    print("Error listing models:", e)
