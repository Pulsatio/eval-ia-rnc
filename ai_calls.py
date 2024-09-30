from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from utils import get_session_required_parameters, get_valid_parameters, createSessionRequest

load_dotenv()

CLIENT = None
CURRENT_STATE = None


def get_client():
    global CLIENT
    if CLIENT is None:
        CLIENT = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return CLIENT

def get_initial_message():
    return "Hola!, soy tu Asistente IA. Estoy para ayudarte a crear sesiones de aprendizaje para los alumnos. ¿En qué puedo ayudarte?"

def prompt():
    validation = get_valid_parameters()
    input_format = '''{ 
    "currentState" : *object or null* , 
    "message" : *text* 
}''' 
    output_format = '''{ 
    "nextState" : *object or null*,
    "answer" : *text*,
    "isFinish" : *boolean* 
}'''
    return f'''
Eres una IA experta en el análisis de texto. Tu principal tarea es ayudar a un docente a crear una sesión de aprendizaje.
 
INPUT FORMAT: (en formato JSON) :
{ input_format }

SALIDA:  (Always respond using the following JSON format)
{ output_format }
Ensure that every response follows this format.



Indicaciones:
- Si el usuario pregunta sobre otro tema que no sea la sesión de aprendizaje responde normalmente.
- Si el usuario quiere crear una sesión se tiene que obtener los parametros siguientes: { ", ".join(get_session_required_parameters())}. Por lo que deberás pedirlos cortésmente. Preferiblemente uno a la vez.
- "Nivel" : los valores permitidos son { validation["Nivel"] }
- "Grado": para el nivel "Inicial" solo pueden tener los grados "3 Años", "4 Años", "5 años"; para el nivel "Primaria" los grados son "Primer grado", "Segundo grado", "Tercer grado", "Cuarto grado", "Quinto grado" y "Sexto grado"; para el nivel "Secundaria" de "Primer año", "Segundo año", "Tercer año", "Cuarto año" y "Quinto año"
- "Sección": los valores permitidos son { validation["Sección"] }
- "Curso": los valores permitidos son { validation["Curso"] }
- Debes asegurarte que los parametros "Nivel" , "Grado" , "Sección" y "Curso" solo contengan los valores permitidos.
- La fecha debe contener dia, mes y año. El año por defecto será 2024. El usuario puede proporcionarla en cualquier formato. Tú debes transformarla al formato dd/mm/yyyy
- El usuario puede proporcionar la hora en cualquier formato. Tu debes transformala al formato hh:mm (24 horas)
- IMPORTANTE: Tienes que construir el "nextState" a partir del "currentState" junto con los atributos que el usuario va agregando o cambiando en su mensaje. No elimines atributos que aparezcan en el "currentState". 
- En el momento en el que "nextState" tenga los atributos { ", ".join(get_session_required_parameters())} tienes que imprimir un listado con los atributos encontrados y pedir una confirmacion de los datos encontrados.
- El "isFinish" solo será verdadero luego de que el usuario confirme aquellos datos, en caso contrario siempre será falso. 

Ejemplos:

1. 
Human: { '{ "currentState" : null , "message" : "Necesito crear una sesión del curso de Matemática para el nivel primaria." }' }
Assistant: {'{  "nextState" :  { "Curso" : "Matemáticas", "Nivel" : "Primaria" }, "answer" : "¡Perfecto! Crearé una sesión para el curso de Matemáticas, ¿Me podrias indicar para que nivel es la sesión?" , "isFinish" : false ' }

2.
Human: { '{ "currentState" : null , "message" : "¿Tu puedes ayudarme a crear una sesión?" }' } 
Assistant: {'{ "nextState" :  null, "answer" : "Sí, con mucho gusto te ayudo a crear una sesión de aprendizaje", "isFinish" : false  }'}

3.
Human: { '{ "currentState" : { "Nivel": 1, "Curso" : "Narrativa" } , "message" : "Es para el curso de Calculo Nuclear" }' } 
Assistant: {'{ "nextState" :  { "Nivel": 1, "Curso" : "Narrativa" } , "answer" : "Disculpa, en mi base de datos no encuentro el curso de Calculo Nuclear, solo puedo crear sesiones con los cursos existentes.", "isFinish" : false  }'}

4. 
Human: { '{ "currentState" : { "Nivel": 1, "Curso" : "Narrativa" } , "message" : "¿Cuanto es 10 + 10?" }' }
Assistant: {'{ "nextState" :  { "Nivel": 1, "Curso" : "Narrativa" }, "answer" : "La respuesta es 20. ¿Prefieres hablar de matemática y dejar la creacion de la sesión para despues?", "isFinish" : false  }'}

5.
Human: { '{ "currentState" : {"Nivel": "Secundaria", "Grado": "Primer Año", "Sección": "Pacha", "Curso": "Química", "Fecha": "27/08/2024", "Hora": "19:00"}, "message" : "El titulo es Quimica 1" }' }
Assistant: { '{ "nextState" :  {"Nivel": "Secundaria", "Grado": "Primer Año", "Sección": "Pacha", "Curso": "Química", "Fecha": "27/08/2024", "Hora": "19:00" , "Titulo" : "Química 1" }, "answer": *Listado de los datos encontrados*  ¿Están correctos todos estos datos?   }' }
''' 
    
def query(message, assistant_message):
    global CURRENT_STATE
   
    client = get_client()    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            assistant_message,
            {"role":"system", "content" : prompt()},
            {"role": "user", "content":  json.dumps({"currentState": CURRENT_STATE, "message": message})}
        ],
    )
    try:
        json_answer = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        return "Hubo un error, por favor vuelva a ingresar su pregunta."

    json_answer = json.loads(response.choices[0].message.content)
    isFinish = json_answer["isFinish"]

    if isFinish:
        response = createSessionRequest(CURRENT_STATE.copy())   
        if response["ok"]:
            CURRENT_STATE = None
        return response["message"]
    
    CURRENT_STATE = json_answer["nextState"]
    if CURRENT_STATE is not None and "Titulo" in CURRENT_STATE:
        CURRENT_STATE["Título"] = CURRENT_STATE["Titulo"]
        del CURRENT_STATE["Titulo"]
    if CURRENT_STATE is not None and "Seccion" in CURRENT_STATE:
        CURRENT_STATE["Sección"] = CURRENT_STATE["Seccion"]
        del CURRENT_STATE["Seccion"]
    return json_answer["answer"]

