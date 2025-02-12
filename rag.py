from openai import OpenAI
import fileToVector
import searchVector
import os

clientQwen = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )

clientOpenAI = OpenAI(
    api_key=os.getenv("LLM_API_KEY")
    )

def responseAssistant(history, nameDB, metric = "cosine", audio_enabled=False, image64 = "", k = 5, modalities = ["text", "audio"]):
    # Crear una copia de la lista para evitar modificar la original
    local_history = history.copy()
    
    DB = fileToVector.loadDB(nameDB)
    
    messUser = local_history[-1]["content"]
    if type(messUser) == list:
        for i in range(len(messUser)):
            if messUser[i]["type"] == "text":
                messUser = messUser[i]["text"]
            elif messUser[i]["type"] == "image_url":
                image64 = messUser[i]["image_url"]["url"]

    print(image64)

    if len(image64) > 0:
        resultContext = searchVector.searchText(messUser, DB, image64=image64, k=k, metric=metric)
    else:
        resultContext = searchVector.searchText(messUser, DB, k=k, metric=metric)
    context = "\n".join(f"{i+1}). {item[1]['text']}" for i, item in zip(range(len(resultContext)), resultContext))
    system = f"""
    Eres un asistente de IA que responde preguntas sobre el siguiente contexto:
    {context}
    Aunque conozcas información fuera de este contexto, no la menciones.
    """
    if local_history[0]["role"] != "system":
        local_history.insert(0, {"role": "system", "content": system})
    else:
        preSystem = local_history[0]["content"]
        local_history[0]["content"] = preSystem + "\n\n" + system


    if audio_enabled:
        response = clientOpenAI.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=modalities,
            audio={"voice": "alloy", "format": "wav"},
            messages=local_history
        )

        return {
            "role": "assistant", 
            "content": response.choices[0].message.audio.transcript, 
            "audio": response.choices[0].message.audio.data,
            "idAudio": response.choices[0].message.audio.id,
            "context": context,
            "tokens_context": int(sum([item[1]["tokens"] for item in resultContext])*0.9),
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens
        }
    elif len(image64) > 0:
        for i in range(len(local_history)):
            if i+1 == len(local_history):
                local_history[i]["content"] = [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image64}"},
                    },
                    {
                        "type" : "text",
                        "text": local_history[i]["content"]
                    }
                ]
            else:
                local_history[-2]["content"] = [
                    {
                        "type" : "text",
                        "text": local_history[-2]["content"]
                    }
                ]
        
        response = clientQwen.chat.completions.create(
            model="qwen-vl-max",
            messages=local_history,
            temperature=0
        )

        return {
            "role": "assistant", 
            "content": response.choices[0].message.content, 
            "context": context,
            "tokens_context": int(sum([item[1]["tokens"] for item in resultContext])*0.9),
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens
        }
    else:
        response = clientQwen.chat.completions.create(
            model="qwen-turbo",
            messages=local_history,
            temperature=0
        )
        return {
            "role": "assistant", 
            "content": response.choices[0].message.content, 
            "context": context,
            "tokens_context": int(sum([item[1]["tokens"] for item in resultContext])*0.9),
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens
        }
