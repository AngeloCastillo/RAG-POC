from flask import Flask, request, jsonify
from flask_cors import CORS


import rag
import fileToVector
import searchVector

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "onLine"

@app.route("/createDB", methods=["POST"])
def createDB():
    data = request.form.to_dict()
    listText = data.get("listText", [])
    fileText = request.files.get("fileText", None)
    model = data.get("model", "text-embedding-v3")
    name = data.get("name", "DB")
    nameRandom = data.get("nameRandom", True)
    withMarker = data.get("withMarker", False)
    marker = data.get("marker", "##")

    # Llamar a la función textToDBVector
    db_name = fileToVector.textToDBVector(
        listText=listText,
        fileText=fileText,
        model=model,
        name=name,
        nameRandom=nameRandom,
        withMarker=withMarker,
        marker=marker
    )

    return jsonify({"db_name": db_name})

@app.route("/search_text", methods=["POST"])
def search_text():
    data = request.json
    text = data.get("text", "")
    DB = data.get("DB", "")
    k = data.get("k", 5)
    metric = data.get("metric", "linalg")
    decimals = data.get("decimals", 3)

    if text == "":
        return jsonify({"error": "Text no debe estar vacio"}), 400
    if DB == "":
        return jsonify({"error": "DB no debe estar vacio"}), 400
    if k == "":
        return jsonify({"error": "k no debe estar vacio"}), 400
    if metric == "":
        return jsonify({"error": "metric no debe estar vacio"}), 400
    if decimals == "":
        return jsonify({"error": "decimals no debe estar vacio"}), 400


    try:
        results = searchVector.searchText(
            text=text,
            DB=DB,
            k=k,
            metric=metric,
            decimals=decimals
        )
        return jsonify({"results": results})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/assistant", methods=["POST"])
def assistant():
    data = request.json
    history = data.get("history", [])
    nameDB = data.get("nameDB", "")
    metric = data.get("metric", "linalg")
    audio_enabled = data.get("audio_enabled", False)
    image64 = data.get("image64", "")
    k = data.get("k", 5)
    modalities = data.get("modalities", ["text", "audio"])

    response = rag.responseAssistant(
        history=history,
        nameDB=nameDB,
        metric=metric,
        audio_enabled=audio_enabled,
        image64=image64,
        k=k,
        modalities=modalities
    )

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
