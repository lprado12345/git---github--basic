from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input="Explain Git and GitHub in one sentence."
)

print(response.output_text)
