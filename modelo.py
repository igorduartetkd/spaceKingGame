#modelo.py

class Modelo:

    def __init__(self, idModelo, velocidadePadrao, arquivo, gp):
        self.__id = idModelo
        self.__velocidadePadrao = velocidadePadrao
        self.__arquivo = arquivo
        self.__gp = gp

    def getId(self):
        return self.__id

    def getVelocidadePadrao(self):
        return self.__velocidadePadrao

    def getArquivo(self):
        return self.__arquivo

    def getGp(self):
        return self.__gp

