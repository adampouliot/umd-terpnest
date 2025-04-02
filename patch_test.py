# patch_test.py
import openai
import instructor
from pydantic import BaseModel

client = instructor.patch(openai.OpenAI())

class Test(BaseModel):
    name: str

result = client.chat.completions.create(
    model="gpt-3.5-turbo",  # 🛠️ Downgraded model
    response_model=Test,
    messages=[{"role": "user", "content": "Name: Adam"}]
)

print(result)
