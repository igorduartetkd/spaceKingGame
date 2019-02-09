import pygame
import Pyro4

pygame.init()
clock = pygame.time.Clock()

print("Buscando salas... ")
salas = {}
n = 1
ipaddr = "192.168.0.4"
port = 7777
with Pyro4.locateNS(host=ipaddr, port=port) as ns:
    for sala, sala_uri in ns.list(prefix="server.spaceking.").items():
        print(n, "- ", sala)
        salas[n] = (Pyro4.Proxy(sala_uri))
        n += 1
if not salas:
    raise ValueError("nenhuma sala encontrada! (iniciar a busca novamente?)")

idSala = int(input("Qual sala deseja se conectar? (posicao): "))
server = salas[idSala]
dicArquivos = server.getModelos()
myNick = input("Informe seu nick: ")
idNaveModelo = 5 + (int(input("Escolha sua nave (1 a 4): ")) % 4)
tela = pygame.display.set_mode((1280, 720))

imgFundo = pygame.image.load("img/fundo.jpg")
imgFundo = pygame.transform.scale(imgFundo, (1280, 720))
rectFundo = imgFundo.get_rect()

fonteNick = pygame.font.SysFont("arial", 20)
fonteLife = pygame.font.SysFont("arial", 30)
idNave, orientacao, posicao = server.criarNave(idNaveModelo, myNick)
print("id nave: ", idNave)
listaImgModelos = {}
for a in dicArquivos:
    arquivo = dicArquivos[a]
    imgModelo = pygame.image.load(arquivo)
    listaImgModelos[a] = pygame.transform.scale(imgModelo, (50, 50))


listaTirosTela = []
listaNavesTela = []

ftpAposMorte = 90

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server.sairSala(idNave)
            pygame.quit()
            exit()

        # Controle de disparos
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                server.atirar(idNave)
                '''
                rectLaser = imagemLaser.get_rect()
                rectLaser.x = rectRocket.x + 100
                rectLaser.y = rectRocket.y
                lista_lasers.append(rectLaser)
                '''

    tecla = pygame.key.get_pressed()

    if tecla[pygame.K_UP]:
        server.movimentar(idNave, 0)

    if tecla[pygame.K_DOWN]:
        server.movimentar(idNave, 180)

    if tecla[pygame.K_LEFT]:
        server.movimentar(idNave, 90)

    if tecla[pygame.K_RIGHT]:
        server.movimentar(idNave, 270)

    # desenhando na tela
    tela.blit(imgFundo, rectFundo)

    listaTirosTela = server.listarTiros()
    listaNavesTela = server.listarNaves()
    vivo = False
    for obj in listaNavesTela:
        idModelo, posicao, orientacao, nick, life = obj
        if myNick == nick:
            vivo = True
        img = listaImgModelos[idModelo]
        rect = img.get_rect()
        rect = rect.move(posicao)
        img = pygame.transform.rotate(img, orientacao)
        tela.blit(img, rect)
        life = str(life)
        nick = fonteNick.render(nick, True, (0,250,154))
        life = fonteLife.render(life, True, (178,34,34))
        posicaoNick = [posicao[0], posicao[1] - 20]
        posicaoLife = [posicao[0] + 5, posicao[1] + 50]
        tela.blit(nick, posicaoNick)
        tela.blit(life, posicaoLife)

    for idModelo, posicao, orientacao in listaTirosTela:
        img = listaImgModelos[idModelo]
        rect = img.get_rect()
        rect = rect.move(posicao)
        img = pygame.transform.rotate(img, orientacao)
        tela.blit(img, rect)

    pygame.display.update()
    if vivo == False:
        if ftpAposMorte == 0:
            break
        ftpAposMorte -= 1
    clock.tick(30)  # 30 FPS
