import openai

openai.api_key = ""

completion = openai.Completion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)
