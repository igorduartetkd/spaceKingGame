#tiro.py
from elemento import Elemento

class Tiro(Elemento):
    ctdId = 1
    def __init__(self, orientacao, posicao, velocidade, idModelo, idNave, poder):
        super().__init__(orientacao, posicao, velocidade, idModelo)
        self.__id = Tiro.ctdId
        Tiro.ctdId += 1
        self.__idNave = idNave
        self.__poder = poder

    def getIdNave(self):
        return self.__idNave

    def getIdTiro(self):
        return self.__id

    def getPoder(self):
        return self.__poder

    def __changePosicao(self, listMovimento):
        novaPosicao = []
        for elemA, elemB in zip(listMovimento, super().getPosicao()):
            novaPosicao.append(elemA + elemB)
        super().setPosicao(novaPosicao)

    def movimentar(self): # direcao em graus
        velocidade = super().getVelocidade()
        traducaoVelocidade = {0: (0, -velocidade), 90: (-velocidade, 0), 180: (0, velocidade), 270: (velocidade, 0)}
        self.__changePosicao(traducaoVelocidade[super().getOrientacao()])