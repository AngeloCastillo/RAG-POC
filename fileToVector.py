import os
from dotenv import load_dotenv
from openai import OpenAI
import formatText
import json
import random
import string
import PyPDF2

# Obtener la clave de la API desde una variable de entorno
load_dotenv()
qwen_api_key = os.getenv("QWEN_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Verificar si la clave de la API está configurada
if not qwen_api_key:
    raise ValueError("La clave de la API del LLM no está configurada. Establece la variable de entorno 'LLM_API_KEY'.")

clientQwen = OpenAI(
    api_key=qwen_api_key,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )

clientOpenAI = OpenAI(
    api_key=openai_api_key,
    )

models = ["text-embedding-v3", "text-embedding-3-small", "text-embedding-3-large"]

# generar un strgin aleatorio alfanumerico con un parametro de longitud
def randomString(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def loadDB(path):
    if ".json" not in path:
        path = path + ".json"
    if "DBs/" not in path:
        path = "DBs/" + path
    if not os.path.exists(path):
        return []
    with open(path, "r") as file:
        return json.load(file)
    
def saveDB(path, data):
    # si el archivo existe, lo lee y actualiza
    if ".json" not in path:
        path = path + ".json"
    if "DBs/" not in path:
        path = "DBs/" + path
    if os.path.exists(path):
        with open(path, "r") as file:
            existing_data = json.load(file)
        
        # Verifica si el contenido existente es una lista
        if isinstance(existing_data, list):
            if isinstance(data, list):
                existing_data.extend(data)  # Agrega cada elemento de la nueva lista
            else:
                existing_data.append(data)  # Agrega el nuevo diccionario
        else:
            raise ValueError("El contenido del archivo no es una lista.")
        
        with open(path, "w") as file:
            json.dump(existing_data, file, indent=4)
    else:
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

def textToVector(text, model = models[0]):
    response = clientQwen.embeddings.create(input=text, model=model)
    return response.data[0].embedding, response.usage.total_tokens

def imageToVector(image64, text = "", model = "qwen2.5-vl-3b-instruct"):
    promtp = """Tu tarea es extraer la información más relevante de la imagen en el formato:
        descripción: una descripción generalde la imagen,
        ORC: todo el texto visible en orden,
        objetos: una lista de objetos visibles en la imagen,
        colores: una lista de colores visibles en la imagen
        """
    response = clientQwen.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": promtp
                        }
                    ]
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image64}"}
                        }
                    ]
                }
            ],
            temperature=0
        )
    
    print(text + "\n\n" + response.choices[0].message.content)

    response, tokens = textToVector(text + "\n\n" + response.choices[0].message.content)
    return response, tokens

def textToDBVector(listText = [], fileText=None, model = models[0], name="DB", nameRandom=True, withMarker=False, marker="##"):
    isPath = False
    if fileText and isinstance(fileText, str):
        if fileText.lower().endswith(".txt"):
            isPath = True
            nameFile = fileText.replace(".txt", "")
            nameFile = nameFile[nameFile.rfind("/")+1:].upper()
            fileText = open(fileText, encoding="utf8").read()
        elif fileText.lower().endswith(".pdf"):
            isPath = True
            nameFile = fileText.replace(".pdf", "")
            nameFile = nameFile[nameFile.rfind("/")+1:].upper()
            with open(fileText, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                fileText = ""
                for page in reader.pages:
                    fileText += page.extract_text()

    if not isPath:
        nameFile = fileText.filename.replace(".txt", "").replace(".pdf", "").upper()
        reader = PyPDF2.PdfReader(fileText)
        fileText = ""
        for page in reader.pages:
            fileText += page.extract_text()

    if withMarker:
        listText = formatText.formatTextMarker(fileText, marker)
    else:
        listText = formatText.formatText(fileText, name)
        

    DB = []
    for text in listText:
        vector, tokens = textToVector(text, model)
        if fileText:
            text = f"{nameFile}\n\n{text}"

        DB.append({"text": text, "vector": vector, "tokens": tokens, "length": len(text)})

    print(nameRandom)
    if nameRandom==True:
        print("entro", nameRandom)
        name = name + "_" + randomString(16)

    # guardar en un archivo json
    saveDB(name + ".json", DB)
    return name
