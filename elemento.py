#elemento.py

class Elemento:

    def __init__(self, orientacao, posicao, velocidade, idModelo):
        self.__orientacao = orientacao
        self.__posicao = posicao
        self.__velocidade = velocidade
        self.__idModelo = idModelo
        self.__escala = [50, 50]

    #getters
    def getOrientacao(self):
        return self.__orientacao

    def getPosicao(self):
        return self.__posicao

    def getVelocidade(self):
        return self.__velocidade

    def getIdModelo(self):
        return self.__idModelo

    def getEscala(self):
        return self.__escala

    #setters
    def setOrientacao(self, orientacao):
        self.__orientacao = orientacao

    def setPosicao(self, posicao):
        self.__posicao = posicao

    def setVelocidade(self, velocidade):
        self.__velocidade = velocidade

    def setIdModelo(self, idModelo):
        self.__idModelo = idModelo

    def setEscala(self, escala):
        self.__escala = escala


    def verificarColisao(self, elemento):
        x = [[0, 0],[0,0]]
        y = [[0, 0],[0,0]]
        x[0][0], x[0][1] = self.__posicao
        y[0][0], y[0][1] = elemento.getPosicao()
        escalax, escalay = self.__escala
        escalax2, escalay2 = elemento.getEscala()
        x[1][0] = x[0][0] + escalax
        x[1][1] = x[0][1] + escalay
        y[1][0] = y[0][0] + escalax2
        y[1][1] = y[0][1] + escalay2

        if x[0][0] > y[1][0] or x[0][1] > y[1][1] or x[1][0] < y[0][0] or x[1][1] < y[0][1]:
            return False

        return True
