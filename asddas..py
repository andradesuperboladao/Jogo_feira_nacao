import pygame
from pygame.locals import *
from sys import exit
import random


pygame.init()
fim = False
largura = 640
altura = 480
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
erros = 0
placar = 0
pygame.font.init()
fonte = pygame.font.SysFont('Arial',40) 

velocidade_y = 2
velocidade_clock = 60




tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Vários Burritos Girando")
class Comida(pygame.sprite.Sprite):
    def __init__(self, imagem, posicao):
        super().__init__()
        self.imagem_original = pygame.transform.scale(imagem, (250, 250))
        self.imagem = self.imagem_original
        self.rect = self.imagem.get_rect(center=posicao)
        self.angulo = 0
        self.y_inicial = altura  # começa embaixo
        self.y_alvo = posicao[1] # sorteado
        self.direcao = -1        # -1: subindo, 1: descendo
    
    def girar(self, angulo):
        self.angulo += angulo
        self.imagem = pygame.transform.rotate(self.imagem_original, self.angulo)
        self.rect = self.imagem.get_rect(center=(self.rect.centerx, self.y_inicial))

    def caiu(self):
        global erros
        x = random.randint(50, largura - 50)
        y = random.randint(50, altura // 2)  # reaparece com alvo aleatório
        self.rect.centerx = x
        self.y_alvo = y
        self.y_inicial = altura
        self.direcao = -1  # volta a subir
        erros +=1

    
    def atualizar(self):
        # Movimento de sobe e desce
        if self.direcao == -1:  # subindo
            if self.y_inicial > self.y_alvo:
                self.y_inicial -= velocidade_y
            else:
                self.direcao = 1
        elif self.direcao == 1:  # descendo
            if self.y_inicial < altura:
                self.y_inicial += velocidade_y
            if self.y_inicial == altura:
                self.caiu()


burrito_imagem = pygame.image.load('l/img/burrito.png')
grupoburritos = pygame.sprite.Group()


for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    burrito = Comida(burrito_imagem, (x, y))
    burrito.rect.centerx = x
    burrito.y_inicial = altura  # começa embaixo
    burrito.y_alvo = y
    grupoburritos.add(burrito)


pimenta_imagem = pygame.image.load('l/img/pimenta.png')
grupopimentas = pygame.sprite.Group()

for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    pimenta = Comida(pimenta_imagem, (x, y))
    pimenta.rect.centerx = x
    pimenta.y_inicial = altura  # começa embaixo
    pimenta.y_alvo = y
    grupopimentas.add(pimenta)

taco_imagem = pygame.image.load('l/img/taco.png')
grupotacos = pygame.sprite.Group()

for _ in range(1):  # 120 fica muito pesado, use menos para testar
    x = random.randint(50, largura - 50)
    y = random.randint(50, altura - 50)
    taco = Comida(taco_imagem, (x, y))
    taco.rect.centerx = x
    taco.y_inicial = altura  # começa embaixo
    taco.y_alvo = y
    grupotacos.add(taco)

clock = pygame.time.Clock()


while True:
    texto = fonte.render(f"erros :{erros}", True, BRANCO)
    texto2 = fonte.render(f"pontuação{placar}", True, BRANCO)
    texto3 = fonte.render("PERDEU LIXO('R' PARA RECOMEÇAR :))", True, BRANCO)
    tela.fill(PRETO)
    tela.blit(texto, (450, 0))
    tela.blit(texto2, (0, 0))

    if erros >= 20:
        tela.fill(VERMELHO)
        fim = True
        tela.blit(texto3, (0, 200))

    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        if event.type == KEYDOWN:
            if event.key == K_r:
                fim = False
                erros = 0

        if event.type == MOUSEBUTTONDOWN and not fim:
            pos_mouse = event.pos
            for burrito in grupoburritos:
                if burrito.rect.collidepoint(pos_mouse):
                    placar +=1
            for pimenta in grupopimentas:
                if pimenta.rect.collidepoint(pos_mouse):
                    print("Pimenta clicada!")
            for taco in grupotacos:
                if taco.rect.collidepoint(pos_mouse):
                    placar +=2

    # --- ATUALIZAÇÃO DOS OBJETOS ---
    if not fim:
        for burrito in grupoburritos:
            burrito.atualizar()
            burrito.girar(1)
            tela.blit(burrito.imagem, (burrito.rect.centerx - burrito.imagem.get_width() // 2, burrito.y_inicial - burrito.imagem.get_height() // 2))

        for pimenta in grupopimentas:
            pimenta.atualizar()
            pimenta.girar(1)
            tela.blit(pimenta.imagem, (pimenta.rect.centerx - pimenta.imagem.get_width() // 2, pimenta.y_inicial - pimenta.imagem.get_height() // 2))

        for taco in grupotacos:
            taco.atualizar()
            taco.girar(1)
            tela.blit(taco.imagem, (taco.rect.centerx - taco.imagem.get_width() // 2, taco.y_inicial - taco.imagem.get_height() // 2))

    pygame.display.update()
    clock.tick(velocidade_clock)
