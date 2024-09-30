class CreateSessionData:
    def __init__(self, strTituloTema: str, fchDesarrollo: str, horInicio: str, strCurso: str, strNivel: str, intGrado: int, codSeccion: str, horFin: str):
        self.strTituloTema = strTituloTema
        self.fchDesarrollo = fchDesarrollo
        self.horInicio = horInicio
        self.strCurso = strCurso
        self.strNivel = strNivel
        self.intGrado = intGrado
        self.codSeccion = codSeccion
        self.horFin = horFin

        # Valores por defecto
        self.idCurso = 1
        self.codArea = "COM"
        self.intNivel = 2
        self.idAula = 14161
        self.intNumeroSesion = 12
        self.codPeriodo = "ivb"
        self.idPersonal = 293
        self.idColegio = 10