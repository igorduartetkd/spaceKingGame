# server.py
import Pyro4
from nave import Nave
from tiro import Tiro
from modelo import Modelo
from random import randint, sample
import pygame
import threading

clock = pygame.time.Clock()

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server(object):
    def __init__(self):
        self.__naves = {}
        self.__tiros = {}
        self.__modelos, self.__modelosTiroPadrao = self.__carregarModelos()

    def getQtdNaves(self):
        return len(self.__naves)

    def criarNave(self, idModelo, nick):
        orientacaoInicial = sample([0, 90, 180, 270], 1)[0] #escolhe uma direcao aleatoria para comecar
        posicaoInicial = [randint(0, 600), randint(0, 600)] #escolhe uma posicao aleatoria para comecar a nave
        velocidade = self.__modelos[idModelo].getVelocidadePadrao()
        nave = Nave(orientacaoInicial,
                    posicaoInicial,
                    velocidade,
                    idModelo,
                    self.__modelosTiroPadrao[idModelo],
                    nick,
                    self.__modelos[idModelo].getGp()
                    )
        print("id nave criado: ", nave.getId())
        self.__naves[nave.getId()] = nave
        return [nave.getId(), nave.getOrientacao(), nave.getPosicao()]

    def criarTiro(self, idNave):
        nave = self.__naves[idNave]
        orientacaoInicial = int(nave.getOrientacao())
        posicaoInicial = nave.getPosicao()
        idModeloTiro = self.__modelosTiroPadrao[nave.getIdModelo()]
        modeloTiro = self.__modelos[idModeloTiro]
        velocidade = modeloTiro.getVelocidadePadrao()
        tiro = Tiro(orientacaoInicial,
                    posicaoInicial,
                    velocidade,
                    idModeloTiro,
                    idNave,
                    modeloTiro.getGp())
        return tiro

    def atirar(self, idNave):
        if idNave in self.__naves:
            tiro = self.criarTiro(idNave)
            self.__tiros[tiro.getIdTiro()] = tiro

    def movimentar(self, idNave, direcao):
        if idNave in self.__naves:
            nave = self.__naves[idNave]
            nave.movimentar(direcao)

    def listarTiros(self):
        saida = []
        for t in self.__tiros:
            tiro = self.__tiros[t]
            saida.append((tiro.getIdModelo(), tiro.getPosicao(), tiro.getOrientacao()))
        return saida

    def listarNaves(self):
        saida = []
        for n in self.__naves:
            nave = self.__naves[n]
            saida.append((nave.getIdModelo(), nave.getPosicao(), nave.getOrientacao(), nave.getNick(), nave.getLife()))
        return saida

    def __carregarModelos(self):
        modelos = {}
        modelosTiroPadrao = {}
        arquivo = open("modelosTiros.txt", 'r')
        i = 1
        for linha in arquivo.readlines():
            linha = linha.split(" ", 3)
            modelo = Modelo(i, int(linha[0]), linha[1], int(linha[2].split('\n')[0]))
            i += 1
            modelos[modelo.getId()] = modelo
            print("modelo tiro: " , modelo.getId())
        arquivo.close()

        arquivo = open("modelosNaves.txt", 'r')
        for linha in arquivo.readlines():
            linha = linha.split(" ", 4)
            modelo = Modelo(i, int(linha[0]), linha[1], int(linha[3].split('\n')[0]))
            i += 1
            modelos[modelo.getId()] = modelo
            modelosTiroPadrao[modelo.getId()] = int(linha[2])
            print("modelo nave: ", modelo.getId())
        arquivo.close()
        return modelos, modelosTiroPadrao

    def getModelos(self):
        saida = {}
        for m in self.__modelos:
            modelo = self.__modelos[m]
            saida[modelo.getId()] = modelo.getArquivo()
        return saida

    def detectarColisao(self, tiro):
        for n in list(self.__naves):
            if tiro.getIdNave() == n:
                continue
            nave = self.__naves[n]
            if tiro.verificarColisao(nave):
                nave.sofrerDano(tiro.getPoder())
                return True
        return False

    def atualizarPosicoes(self):
        for t in list(self.__tiros):
            tiro = self.__tiros[t]
            (x, y) = tiro.getPosicao()
            if x < 0 or y < 0 or x > 1900 or y > 1000:
                del self.__tiros[t]
                continue
            if self.detectarColisao(tiro):
                del self.__tiros[t]
                continue
            tiro.movimentar()

        for n in list(self.__naves):
            nave = self.__naves[n]
            if nave.getLife() <= 0:
                del self.__naves[n]

    def sairSala(self, idNave):
        del self.__naves[idNave]



def main():
    ipaddr = "192.168.0.4"
    port = 7777
    Pyro4.config.HOST = ipaddr
    Pyro4.config.NS_PORT = port
    server1 = Server()
    server2 = Server()
    daemon = Pyro4.Daemon()
    uri1 = daemon.register(server1)
    uri2 = daemon.register(server2)
    ns = Pyro4.locateNS(host=ipaddr, port=port)
    ns.register("server.spaceking.1", uri1)
    ns.register("server.spaceking.2", uri2)
    t = threading.Thread(target=daemon.requestLoop)
    t.start()
    while True:
        if server1.getQtdNaves():
            server1.atualizarPosicoes()
        if server2.getQtdNaves():
            server2.atualizarPosicoes()
        clock.tick(30)  # 30 FPS


if __name__=="__main__":
    main()
