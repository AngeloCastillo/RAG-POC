def unirTextos(listText):
    for i in range(1, len(listText)):
        if len(listText[i]) + len(listText[i-1]) <= 1500:
            listText[i-1] += " " + listText[i]
            del listText[i]
            break
    return listText

def formatText(text, nameFile):
    listText = text.split("\n")
    listText = [item.strip() for item in listText if len(item.strip()) > 0]
    while any(len(item) < 100 for item in listText):
        lenInit = len(listText)
        listText = unirTextos(listText)
        if lenInit == len(listText):
            break

    # si un texto supero los 2000 caracteres, se divide en dos, pero se separa por palabras
    while any(len(item) > 2000 for item in listText):
        for i in range(len(listText)):
            if len(listText[i]) > 2000:
                listUniText = listText[i].split(" ")
                divis = round(len(listText[i])/1000)
                step = int(len(listUniText)/divis)
                for j in range(divis):
                    listText.insert(i+1+j, " ".join(listUniText[j*step:(j+1)*step]))
                del listText[i]
                break
    # listText = [f"{nameFile}\n\n{item}" for item in listText]
    return listText

def formatTextMarker(text, marker):
    listText = text.split(marker)
    listText = [item.strip() for item in listText if len(item.strip()) > 0]
    return listText
