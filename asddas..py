import pygame
from pygame.locals import *
from sys import exit
import random


pygame.init()
fim = False
altura,largura = 600,800
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
erros = 0
placar = 0
estado = "menu" # "menu" ou "jogo"
ranking = 0
pygame.font.init()
fonte = pygame.font.SysFont('Sans-serif',40) 

velocidade_y = 2


velocidade_clock = 60


# --- VARIÁVEIS DE BOOST PIMENTA---
boost_ativo = False
tempo_boost = 0
duracao_boost = 5000   # 5 segundos em ms
velocidade_base = velocidade_y  # guarda a velocidade normal

#--- TELA ----
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Vários Burritos Girando")

#--- CLASSE COMIDA ----
class Comida(pygame.sprite.Sprite):
    def __init__(self, imagem, posicao, tipo="normal"):
        super().__init__()
        self.imagem_original = pygame.transform.scale(imagem, (300, 300))
        self.imagem = self.imagem_original
        self.rect = self.imagem.get_rect(center=posicao)
        self.mask = pygame.mask.from_surface(self.imagem) # máscara para colisão
        self.angulo = 0
        self.y_inicial = altura  # começa embaixo
        self.y_alvo = posicao[1] # sorteado
        self.direcao = -1        # -1: subindo, 1: descendo
        self.tipo = tipo # "normal""bomba"

        # Variáveis de controle do tempo de reset
        self.esperando_reset = False
        self.tempo_retorno = 0

        if self.tipo == "bomba":
            self.imagem_original = pygame.transform.scale(imagem, (100, 100))
            self.rect = self.imagem_original.get_rect(center=posicao)
            self.mask = pygame.mask.from_surface(self.imagem_original) # máscara para colisão
    
    def girar(self, angulo):
        self.angulo += angulo
        self.imagem = pygame.transform.rotate(self.imagem_original, self.angulo)
        self.rect = self.imagem.get_rect(center=(self.rect.centerx, self.y_inicial))
        self.mask = pygame.mask.from_surface(self.imagem)  # atualizar máscara após rotação

    def caiu(self):
        # Ativa o tempo de espera antes de voltar
        if not self.esperando_reset:
            self.esperando_reset = True
            delay = random.randint(500, 5000)  # delay aleatório entre 0,5 e 5 segundos
            self.tempo_retorno = pygame.time.get_ticks() + delay

            #Aumenta se n for BOMBA
            if self.tipo != "bomba":
                global erros
                erros +=1

    def resetar(self):
        # calcula delay baseado na pontuação
        max_delay = 5000  # 5 segundos
        min_delay = 500   # 0,5 segundo

        # diminui delay conforme placar
        if placar >= 100:
            max_delay = 2000
        elif placar >= 50:
            max_delay = 3000
        elif placar >= 20:
            max_delay = 4000
        elif placar >= 10:
            max_delay = 4500

        # se ainda não está esperando, ativa o tempo de espera
        if not self.esperando_reset:
            self.esperando_reset = True
            delay = random.randint(min_delay, max_delay)
            self.tempo_retorno = pygame.time.get_ticks() + delay

        # só reseta quando o tempo tiver passado
        if self.esperando_reset and pygame.time.get_ticks() >= self.tempo_retorno:
            self.rect.centerx = random.randint(50, largura - 50)
            self.y_alvo = random.randint(50, altura // 2)
            self.y_inicial = altura
            self.direcao = -1  # volta a subir  
            self.esperando_reset = False  # pronto pra próxima queda

    def atualizar(self):
        # Se está esperando, não mostra o objeto
        if self.esperando_reset:
            # opcional: move o objeto fora da tela enquanto espera
            self.y_inicial = altura + 100  # fora da tela
            self.resetar()  # verifica se já pode voltar
            return

        # Movimento de sobe e desce
        if self.direcao == -1:  # subindo
            if self.y_inicial > self.y_alvo:
                self.y_inicial -= velocidade_y
            else:
                self.direcao = 1
        elif self.direcao == 1:  # descendo
            if self.y_inicial < altura:
                self.y_inicial += velocidade_y
            if self.y_inicial >= altura: #garante que não fique travado
                self.y_inicial = altura
                self.caiu()




#----- CARREGAR IMAGENS ------
burrito_imagem = pygame.image.load("img/burrito.png")
pimenta_imagem = pygame.image.load('img/pimenta.png')
taco_imagem = pygame.image.load('img/taco.png')
bomba_imagem = pygame.image.load("img/caveira_jogo.png")


#--------- GRUPOS -----
grupotacos = pygame.sprite.Group()
grupoburritos = pygame.sprite.Group()
grupopimentas = pygame.sprite.Group()
grupobombas = pygame.sprite.Group()


#--- BURRITO
for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    burrito = Comida(burrito_imagem, (x, y), tipo="normal")
    burrito.rect.centerx = x
    burrito.y_inicial = altura  # começa embaixo
    burrito.y_alvo = y
    grupoburritos.add(burrito)

#--- BOMBA CAVEIRA
for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    bomba = Comida(bomba_imagem, (x, y), tipo="bomba")
    bomba.rect.centerx = x
    bomba.y_inicial = altura
    bomba.y_alvo = y
    grupobombas.add(bomba)

#----- PIMENTA
for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    pimenta = Comida(pimenta_imagem, (x, y), tipo="normal")
    pimenta.rect.centerx = x
    pimenta.y_inicial = altura  # começa embaixo
    pimenta.y_alvo = y
    grupopimentas.add(pimenta)


#----- TACO
for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    taco = Comida(taco_imagem, (x, y), tipo="normal")
    taco.rect.centerx = x
    taco.y_inicial = altura  # começa embaixo
    taco.y_alvo = y
    grupotacos.add(taco)

# TEMPO REAL DOS OBJETOS
clock = pygame.time.Clock()


# MENU INICIAL
def desenhar_menu():
    tela.fill(PRETO)

    # TÍTULO E TEXTOS
    titulo = fonte.render("CAVEIRAS", True, BRANCO)
    jogar = fonte.render("JOGAR", True, BRANCO)
    credito = fonte.render("By NATADO2AI", True, BRANCO)

    tela.blit(titulo, (largura//2 - titulo.get_width()//2, 100))

    #BOTÃO JOGAR
    botao = pygame.Rect(largura//2 - 100, altura//2 - 30, 200, 60)
    pygame.draw.rect(tela, BRANCO, botao, 2)
    tela.blit(jogar, (largura//2 - jogar.get_width()//2, altura//2 - jogar.get_height()//2))

    #CRÉDITO
    tela.blit(credito, (largura//2 - credito.get_width()//2, altura - 50))
    
    # Carregar e redimensionar caveira proporcionalmente à altura da tela
    caveira_original_menu = pygame.image.load("img/caveira.png").convert()
    caveira_menu = pygame.transform.scale(caveira_original_menu, (200, 200))

    #POSICIONAR CAVEIRAS NOS CANTOS
    tela.blit(caveira_menu, (-20, 25))  # Canto superior esquerdo
    tela.blit(caveira_menu, (largura - caveira_menu.get_width(), 25))  # Canto superior direito


    return botao



# -------- EVENTOS -----
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        if estado == "menu":
            if event.type == MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(event.pos):
                    estado = "jogo"

        elif estado == "jogo":
            if event.type == KEYDOWN:
                if event.key == K_r and fim:
                    fim = False
                    erros = 0
                    placar = 0
                estado = "menu"
                    
                    


            if event.type == MOUSEBUTTONDOWN and not fim:
                pos_mouse = event.pos
                # Ajusta a velocidade dos objetos conforme o placar
                if placar >= 100:
                    velocidade_y = velocidade_base * 2.7
                elif placar >= 50:
                    velocidade_y = velocidade_base * 2.3
                elif placar >= 20:
                    velocidade_y = velocidade_base * 2
                elif placar >= 10:
                    velocidade_y = velocidade_base * 1.7
                else:
                    velocidade_y = velocidade_base


                for burrito in grupoburritos:
                    offset = (pos_mouse[0] - burrito.rect.left, pos_mouse[1] - burrito.rect.top)
                    if 0 <= offset[0] < burrito.rect.width and 0 <= offset[1] < burrito.rect.height:
                            if burrito.mask.get_at(offset):  # ✅ verifica pixel visível
                                placar += 1
                                burrito.resetar()

                for pimenta in grupopimentas:
                    offset = (pos_mouse[0] - pimenta.rect.left, pos_mouse[1] - pimenta.rect.top)
                    if 0 <= offset[0] < pimenta.rect.width and 0 <= offset[1] < pimenta.rect.height:
                        if pimenta.mask.get_at(offset):
                            boost_ativo = True
                            tempo_boost = pygame.time.get_ticks()
                            velocidade_y = velocidade_base * 2
                            pimenta.resetar()

                for taco in grupotacos:
                    offset = (pos_mouse[0] - taco.rect.left, pos_mouse[1] - taco.rect.top)
                    if 0 <= offset[0] < taco.rect.width and 0 <= offset[1] < taco.rect.height:
                        if taco.mask.get_at(offset):
                            placar += 2
                            taco.resetar()

                for bomba in grupobombas:
                    offset = (pos_mouse[0] - bomba.rect.left, pos_mouse[1] - bomba.rect.top)
                    if 0 <= offset[0] < bomba.rect.width and 0 <= offset[1] < bomba.rect.height:
                        if bomba.mask.get_at(offset):
                            fim = True
                            erros = 10
                            bomba.resetar()


    # --- DESENHO ---
    if estado == "menu":
        botao_jogar = desenhar_menu()
        if event.type == MOUSEBUTTONDOWN:
            if botao_jogar.collidepoint(event.pos):
                estado = "jogo"

    elif estado == "jogo":
        texto = fonte.render(f"erros {erros}", True, BRANCO)
        texto2 = fonte.render(f"pontuação {placar}", True, BRANCO)
        texto3 = fonte.render("PERDEU ('R' P/ RECOMEÇAR)", True, BRANCO)
        texto4 = fonte.render(f"Parabéns novo recorde atingido, o recorde agora é de {ranking}", True, BRANCO)
        tela.fill(PRETO)
        tela.blit(texto, (450, 0))
        tela.blit(texto2, (0, 0))

        if erros >= 10:
            tela.fill(VERMELHO)
            fim = True
            tela.blit(texto3, (150, 200))
            if placar > ranking:
                ranking = placar
                tela.blit(texto4,(150,150))

        if boost_ativo:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - tempo_boost >= duracao_boost:
                velocidade_y = velocidade_base
                boost_ativo = False

        if not fim:
            for burrito in grupoburritos:
                burrito.atualizar()
                burrito.girar(1)
                tela.blit(burrito.imagem, (burrito.rect.centerx - burrito.imagem.get_width() // 2,
                                           burrito.y_inicial - burrito.imagem.get_height() // 2))


            for pimenta in grupopimentas:
                pimenta.atualizar()
                pimenta.girar(1)
                tela.blit(pimenta.imagem, (pimenta.rect.centerx - pimenta.imagem.get_width() // 2,
                                           pimenta.y_inicial - pimenta.imagem.get_height() // 2))


            for taco in grupotacos:
                taco.atualizar()
                taco.girar(1)
                tela.blit(taco.imagem, (taco.rect.centerx - taco.imagem.get_width() // 2,
                                        taco.y_inicial - taco.imagem.get_height() // 2))


            for bomba in grupobombas:
                bomba.atualizar()
                bomba.girar(1)
                tela.blit(bomba.imagem, (bomba.rect.centerx - bomba.imagem.get_width() // 2,
                                 bomba.y_inicial - bomba.imagem.get_height() // 2))

    if placar >= 100:
        velocidade_clock = 90
    elif placar >= 50:
        velocidade_clock = 75
    elif placar >= 20:
        velocidade_clock = 70
    elif placar >= 10:
        velocidade_clock = 65

    pygame.display.update()
    clock.tick(velocidade_clock)