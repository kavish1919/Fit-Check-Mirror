import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=api_key)

try:
    models = client.models.list()
    with open('models.txt', 'w') as f:
        for model in models.data:
            f.write(f"{model.id}\n")
    print("Models written to models.txt")
except Exception as e:
    print(f"Error: {e}")
