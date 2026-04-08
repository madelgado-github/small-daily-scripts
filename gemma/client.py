from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

MODEL = "gemma3:1b"
history = []

print(f"Gemma3 Chat ({MODEL}) — escribe 'salir' para terminar\n")

while True:
    user_input = input("Tu: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "salir":
        break

    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    print(f"\nGemma: {reply}\n")
