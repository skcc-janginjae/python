from openai import OpenAI

client = OpenAI(api_key="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")


completion = client.chat.completions.create(
    model="gpt-4o",
    store=True,
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)


print(completion.choices[0].message.content)
