import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()

client = Cerebras(
    # This is the default and can be omitted
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

stream = client.chat.completions.create(
    messages=[{"role": "system", "content": "hello"}],
    model="qwen-3-235b-a22b-instruct-2507",
    stream=True,
    max_completion_tokens=32768,
    temperature=0.6,
    top_p=0.9,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
