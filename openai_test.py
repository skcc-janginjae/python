import openai

openai.api_key = "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"

completion = openai.Completion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)
