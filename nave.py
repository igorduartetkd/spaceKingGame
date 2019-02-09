#nave.py
from elemento import Elemento


listaModelosNaves = ("img/nave1.png", "img/nave2.png", "img/nave3.png", "img/nave4.png")
velocidadeNaves = {1: 15, 2: 15, 3: 15, 4: 20}

class Nave(Elemento):
    ctdId = 1
    def __init__(self, orientacao, posicao, velocidade, idModelo, idTiroPadrao, nick, life):
        super().__init__(orientacao, posicao, velocidade, idModelo)
        self.__id = Nave.ctdId
        Nave.ctdId += 1
        self.__idTiroPadrao = idTiroPadrao
        self.__nick = str(nick)
        self.__life = life

    def getId(self):
        return self.__id

    def getIdTiroPadrao(self):
        return self.__idTiroPadrao

    def getLife(self):
        return self.__life

    def setIdTiroPadrao(self, idModeloTiro):
        self.__idTiroPadrao = idModeloTiro

    def getNick(self):
        return self.__nick

    def __changePosicao(self, listMovimento):
        novaPosicao = []
        for elemA, elemB in zip(listMovimento, super().getPosicao()):
            novaPosicao.append(elemA + elemB)
        super().setPosicao(novaPosicao)

    def movimentar(self, direcao): # direcao em graus
        orientacaoRotate = direcao - super().getOrientacao()
        super().setOrientacao(direcao)
        velocidade = super().getVelocidade()
        traducaoVelocidade = {0: (0, -velocidade), 90: (-velocidade, 0), 180: (0, velocidade), 270: (velocidade, 0)}
        self.__changePosicao(traducaoVelocidade[direcao])

    def sofrerDano(self, dano):
        self.__life -= dano