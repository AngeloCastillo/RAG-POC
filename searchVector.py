import numpy as np
import fileToVector

def searchText(text, DB, image64 = "", k = 5, metric = "linalg", decimals = 3):
    if isinstance(DB, str):
        DB = fileToVector.loadDB(DB)
    print(image64)
    if len(image64) > 0:
        vector, tokens = fileToVector.imageToVector(image64, text)
    else:
        vector, tokens = fileToVector.textToVector(text)
    if metric == "linalg":
        return metricLinalg(DB, vector)[:k]
    elif metric == "cosine":
        return metricCosine(DB, vector)[:k]
    elif metric == "jaccard":
        return metricJaccard(DB, vector, decimals)[:k]
    elif metric == "hamming":
        return metricHamming(DB, vector, decimals)[:k]
    else:
        raise ValueError("Metric no encontrada")

def metricLinalg(DB, vector):
    distances = [np.linalg.norm(np.array(vector) - np.array(item["vector"])) for item in DB]
    return sorted(zip(distances, DB), key=lambda x: x[0])

def metricCosine(DB, vector):
    distances = [np.dot(np.array(vector), np.array(item["vector"])) / (np.linalg.norm(np.array(vector)) * np.linalg.norm(np.array(item["vector"]))) for item in DB]
    return sorted(zip(distances, DB), key=lambda x: x[0], reverse=True)

def metricJaccard(DB, vector, numDecimals = 3):
    vector = [round(i, numDecimals) for i in vector]
    DB = [{"text": item["text"], 
           "vector": [round(j, numDecimals) for j in item["vector"]],
           "tokens" : item["tokens"],
           "length": item["length"]
           } for item in DB]
    distances = [len(set(vector) & set(item["vector"])) / len(set(vector) | set(item["vector"])) for item in DB]
    return sorted(zip(distances, DB), key=lambda x: x[0], reverse=True)

def metricHamming(DB, vector, numDecimals = 3):
    vector = [round(i, numDecimals) for i in vector]
    DB = [{"text": item["text"], 
           "vector": [round(j, numDecimals) for j in item["vector"]],
           "tokens" : item["tokens"],
           "length": item["length"]
           } for item in DB]
    # Esta métrica no es simétrica, por lo que no es recomendable usarla
    distances = [np.sum(np.array(vector) != np.array(item["vector"])) for item in DB]
    return sorted(zip(distances, DB), key=lambda x: x[0])

