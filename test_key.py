from dotenv import load_dotenv
import os

load_dotenv()

clave = os.getenv("GROQ_API_KEY")

print(clave)
print(len(clave))