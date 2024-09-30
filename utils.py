import json
import re
from datetime import datetime, timedelta
from classes import CreateSessionData
import requests
from dotenv import load_dotenv
import os

load_dotenv()

VALID_PARAMETERS = None
VALIDATION_DATA = None

def get_session_required_parameters():
    return [ "Nivel", "Grado", "Sección", "Curso", "Fecha", "Hora", "Título" ]

def get_validation_data():
    global VALIDATION_DATA
    if VALIDATION_DATA is None:
        try:
            file = open('validation.json')
            VALIDATION_DATA = json.load(file)
        except:
            print('No se ha encontrado el archivo de validación')
            return  
    return VALIDATION_DATA

def get_valid_parameters():
    global VALID_PARAMETERS
    if VALID_PARAMETERS is not None:
        return VALID_PARAMETERS      
    validation_data = get_validation_data() 
    validation = {
        "Nivel": [ nivel["strNivel"]for nivel in validation_data["aNivel"].values()] ,
        "Grado": [  grado["strGrado"]  for nivel in validation_data["aNivel"].values() for grado in nivel["aGrado"].values()] ,
        "Sección": list(set([ aula["codSeccion" ] for aula in validation_data["aAula"].values()])),
        "Curso" : list(set([ curso["strNombre"]  for curso in validation_data["aCurso"].values() ]))
    }
    VALID_PARAMETERS = validation
    return validation



def check_parameters(nivel:str, grado: str, seccion:str, curso:str):
    valid_parameters = get_valid_parameters()
   
    if nivel not in valid_parameters["Nivel"]:
        return f"Mil disculpas. Creo que he ingresado un nivel inválido. Por favor ingrese uno de los siguientes niveles: " + ", ".join(valid_parameters["Nivel"])
    if grado not in valid_parameters["Grado"]:
        return f"Al parecer ingresó un grado inválido. Por favor ingrese uno de los siguientes grados: " + ", ".join(valid_parameters["Grado"])
    if seccion not in valid_parameters["Sección"]:
        return f"Al parecer ingresó una sección inválida. Por favor ingrese una de los siguientes secciones: " + ", ".join(valid_parameters["Sección"])
    if curso not in valid_parameters["Curso"]:
        return f"Al parecer ingresó un curso inválido. Por favor ingrese uno de los siguientes cursos: " + ", ".join(valid_parameters["Curso"])
     
    
    intNivel = -1
    intGrado = -1
    validation_data = get_validation_data()

    for nivelData in validation_data["aNivel"].values():
        if nivelData["strNivel"] == nivel:
            intNivel = nivelData["intNivel"]
            for gradoData in nivelData["aGrado"].values():
                if gradoData["strGrado"] == grado:
                    intGrado = gradoData["intGrado"]
            if intGrado == -1:
                return f"Al parecer ingresó un grado inválido. Por favor ingrese uno de los siguientes grados para el nivel seleccionado: " +  ", ".join([ gradoData["strGrado"] for gradoData in nivelData["aGrado"]])

    if intNivel == -1:
        return f"Al parecer ingresó un nivel inválido. Por favor ingrese uno de los siguientes niveles: " + ", ".join( [ nivel["strNivel"]for nivel in validation_data["aNivel"].values()] )
    
    validAula = False
    for aula in validation_data["aAula"].values():
        if aula["intNivel"] == intNivel and aula["intGrado"] == intGrado and aula["codSeccion"] == seccion:
            validAula = True
            
    if not validAula:
        validSecciones = [ aula["codSeccion"] for aula in validation_data["aAula"].values() if aula["intNivel"] == intNivel and aula["intGrado"] == intGrado]
        if len(validSecciones) == 0:
            return f"En mi base de datos no he encontrado secciones para el nivel {nivel} y grado {grado} seleccionados. Por favor ingrese otro nivel y grado."
        return f"En mi base de datos no he encontrado una sección para el nivel y grado seleccionados. Las secciones validas para el nivel {nivel} y grado {grado} son: " +  ", ".join(validSecciones) + ". Por favor ingrese una sección valida"

    validCurso = False
    
    for cursoData in validation_data["aCurso"].values():
        if cursoData["intNivel"] == intNivel and cursoData["intGrado"] == intGrado and cursoData["strNombre"] == curso:
            validCurso = True
            
    if not validCurso:
        validCursos =  [cursoData["strNombre"] for cursoData in validation_data["aCurso"].values() if cursoData["intNivel"] == intNivel and cursoData["intGrado"] == intGrado]
        if len(validCursos) == 0:
            return  f"En mi base de datos no he encontrado cursos para el nivel {nivel} y grado {grado} seleccionados. Por favor ingrese otro nivel y grado."
        return f"En mi base de datos no he encontrado un curso para el nivel y grado seleccionados. Los cursos para el nivel {nivel} y grado {grado} son: " +  ", ".join([ cursoData["strNombre"] for cursoData in validation_data["aCurso"].values() if cursoData["intNivel"] == intNivel and cursoData["intGrado"] == intGrado]) + ". Por favor ingrese una sección valida"

    return None

def createSessionRequest(data: dict):
    request_url =  os.environ["CREATE_SESSION_URL_ENDPOINT"]
    
    # Verificar existencia
    if "Nivel" not in data:
        return { "message": "Hubo un problema al ingresar el nivel. ¿Podría indicarme de nuevo el nivel?", "ok" : False }
    if "Grado" not in data:
        return { "message": "Hubo un problema al ingresar el grado. ¿Podría indicarme de nuevo el grado?", "ok": False }
    if "Sección" not in data:
        return { "message": "Hubo un problema al ingresar la sección. ¿Podría indicarme de nuevo la sección?", "ok" : False }
    if "Curso" not in data:
        return { "message": "Hubo un problema al ingresar el curso. ¿Podría indicarme de nuevo el curso?", "ok" : False }
    if "Título" not in data:
        return { "message": "Hubo un problema al ingresar el título. ¿Podría indicarme de nuevo el título?", "ok" : False }
    if "Fecha" not in data:
        return { "message": "Hubo un problema al ingresar la fecha. ¿Podría indicarme de nuevo la fecha?", "ok" : False }
    if "Hora" not in data:
        return { "message": "Hubo un problema al ingresar la hora. ¿Podría indicarme de nuevo la hora?", "ok" : False }
    
    # Verificar datos
    message = check_parameters(data["Nivel"], data["Grado"], data["Sección"], data["Curso"])
    
    if message is not None:
        return { "message":message, "ok": False }

    # Verificar fecha
    if not re.match( r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$", data["Fecha"]):
        return { "message": "La fecha es inválida. ¿Podría indicarme de nuevo la fecha?", "ok" : False }
    
    # Verificar hora
    if not re.match( r"^([01][0-9]|2[0-3]):([0-5][0-9])$", data["Hora"]):
        return { "message": "La hora es inválida. ¿Podría indicarme de nuevo la hora?", "ok" : False }
    
    gradoParser = {"3": 3, "4": 4 , "5": 5, "Primer" : 1, "Segundo" : 2, "Tercer": 3, "Cuarto": 4, "Quinto": 5, "Sexto": 6 }
    intGrado = None
    for key in gradoParser:
        if key in data["Grado"]:
            intGrado = gradoParser[key]
            break
    if intGrado is None:
        return { "message": "El grado proporcionado no es válido. ¿Podría indicarme de nuevo el grado?", "ok": False }
    

    
    horFin = (datetime.strptime(data["Hora"], "%H:%M") + timedelta(hours=1)).strftime("%H:%M")

    createSessionData = CreateSessionData(
        strTituloTema=data["Título"],
        fchDesarrollo=data["Fecha"],
        horInicio=data["Hora"],
        strCurso=data["Curso"],
        strNivel=data["Nivel"],
        intGrado=intGrado,
        codSeccion=data["Sección"],
        horFin=horFin
    )

    try:
        response = requests.post(request_url, json=createSessionData.__dict__)
       
        if response.status_code == 200:
            return { "message": "La sesión ha sido creada. ¿Desea crear otra sesión de aprendizaje?", "ok": True }
        else:
            return { "message": "Ha ocurrido un error. Por favor intentelo nuevamente o más tarde.", "ok": False }

    except requests.exceptions.RequestException as e:
        
        return { "message": "Error en la solicitud. Por favor intentelo más tarde.", "ok": False }

