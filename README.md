La aplicación estará disponible en `http://0.0.0.0:5000`.

## Rutas de la API

### `GET /`

Devuelve un mensaje simple para verificar que el servidor está en línea.

### `POST /createDB`

Crea una base de datos vectorial a partir de texto o archivos.

- **Parámetros del formulario:**
  - `listText`: Lista de textos para convertir en vectores. (no es nevesario si se proporciona un archivo)
  - `fileText`: Archivo de texto o PDF para convertir en vectores. (no es nevesario si se proporciona una lista de textos)
  - `model`: Modelo de embedding a utilizar (por defecto `text-embedding-v3`).
  - `name`: Nombre de la base de datos. (no es necesario la extension .json)
  - `nameRandom`: Booleano para agregar una cadena aleatoria al nombre de la base de datos.
  - `withMarker`: Booleano para usar un marcador en el texto. Se usará para cortar el texto en partes.
  - `marker`: Marcador a usar en el texto.

- **Respuesta:**
  - `db_name`: Nombre de la base de datos creada.

### `POST /search_text`

Busca texto en una base de datos vectorial.

- **Parámetros JSON:**
  - `text`: Texto a buscar.
  - `DB`: Nombre de la base de datos.
  - `k`: Número de resultados a devolver.
  - `metric`: Métrica de similitud vectorial (por defecto `cosine`).
  - `decimals`: Precisión decimal para ciertas métricas. (solo para jaccard y hamming)

- **Respuesta:**
  - `results`: Resultados de la búsqueda.

### `POST /assistant`

Proporciona respuestas basadas en un contexto dado.

- **Parámetros JSON:**
  - `history`: Historial de mensajes. (obligatorio)
  - `nameDB`: Nombre de la base de datos.
  - `metric`: Métrica de similitud vectorial.
  - `audio_enabled`: Booleano para habilitar respuestas de audio. (funciona solo con api de OpenAI)
  - `image64`: Imagen en base64 para análisis.
  - `k`: Número de resultados contextuales.
  - `modalities`: Modalidades de respuesta (texto, audio). (solo se audio_enabled=True)

- **Respuesta:**
  - Respuesta del asistente con contexto, textos resultados de similitud vectorial, opcionalmente, audio.

Se incluye un ejemplo de uso en el archivo `test.ipynb`.