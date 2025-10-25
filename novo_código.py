import pygame
import random
import math
from pygame.locals import *
from sys import exit

pygame.init()
pygame.font.init()

# --- CONFIGURAÇÕES BÁSICAS ---
tamanhoTela = pygame.display.get_desktop_sizes()[0] 
largura, altura = tamanhoTela # (largura, altura)
tela = pygame.display.set_mode(tamanhoTela)
pygame.display.set_caption("Slice Of Sinaloa ⚔️")

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)

fonte = pygame.font.SysFont('Sans-serif', 36)
clock = pygame.time.Clock()

# --- CARREGAR IMAGENS ---
burrito_img = pygame.image.load("img/burrito.png")
bomba_img = pygame.image.load("img/caveira_jogo.png")
taco_img = pygame.image.load("img/taco.png")
pimenta_img = pygame.image.load("img/pimenta.png")


# --- VARIÁVEIS DE JOGO ---

logi = open("rankinglog.txt","a+", encoding="utf-8")
logi.seek(0)
linhas = logi.readlines()
pontuacoes = [int(l.strip()) for l in linhas if l.strip()]
maiorpontuacao = max(pontuacoes) if pontuacoes else 0
logi.close()
estado = "menu"
placar = 0
vidas = 3
objetos = []
ultimo_lancamento = 0
intervalo_lancamento = 800  # ms
mouse_trilha = []

# --- FUNÇÕES AUXILIARES ---
def desenhar_menu():
    tela.fill(PRETO)

    # TÍTULO E TEXTOS
    titulo = fonte.render("MEXICO NINJA", True, BRANCO)
    jogar = fonte.render("JOGAR", True, BRANCO)
    credito = fonte.render("By NATADO2AI", True, BRANCO)
    melhor = fonte.render(f"TOP RANKING:{maiorpontuacao}", True, BRANCO)

    tela.blit(titulo, (largura//2 - titulo.get_width()//2, 100))
    tela.blit(melhor, (largura//2 - melhor.get_width()//2, 200))
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

def lancar_objeto():
    tipo = random.choice(["burrito", "taco", "pimenta", "bomba"])
    if tipo == "burrito":
        imagem = burrito_img
    elif tipo == "taco":
        imagem = taco_img
    elif tipo == "pimenta":
        imagem = pimenta_img
    else:
        imagem = bomba_img

    imagem = pygame.transform.scale(imagem, (300, 380))
    mascara = pygame.mask.from_surface(imagem)

    # Lançar de baixo para cima
    x = random.randint(100, largura - 100)
    y = altura + 50  # começa fora da tela
    velocidade_x = random.uniform(-4, 4)
    velocidade_y = random.uniform(-32, -25)  # controla altura máxima
    gravidade = 0.5  # controla a queda

    obj = {
        "tipo": tipo,
        "imagem": imagem,
        "mascara": mascara,
        "x": x, "y": y,
        "vel_x": velocidade_x,
        "vel_y": velocidade_y,
        "grav": gravidade,
        "ativo": True
    }

    objetos.append(obj)

def desenhar_texto(texto, pos, cor=BRANCO):
    t = fonte.render(texto, True, cor)
    tela.blit(t, pos)

# --- LOOP PRINCIPAL ---
rodando = True

while rodando:
    # --- MENU PRINCIPAL ---
    if estado == "menu":
        botao_jogar = desenhar_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(event.pos):
                    estado = "jogo"
                    placar = 0
                    vidas = 3
                    objetos.clear()
                    ultimo_lancamento = pygame.time.get_ticks()

    # --- JOGO RODANDO ---
    elif estado == "jogo":
        tela.fill(PRETO)
        teclas = pygame.key.get_pressed()
        tempo_atual = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if teclas[pygame.K_x]:
                rodando = False

        # --- Lançar novos objetos periodicamente ---
        if tempo_atual - ultimo_lancamento > intervalo_lancamento:
            lancar_objeto()
            ultimo_lancamento = tempo_atual
            intervalo_lancamento = random.randint(600, 1200)

        # --- Atualizar e desenhar objetos ---
        for obj in objetos:
            if obj["ativo"]:
                obj["x"] += obj["vel_x"]
                obj["y"] += obj["vel_y"]
                obj["vel_y"] += obj["grav"]

                # Se o objeto sair da tela e for comestível → perde vida
                if obj["y"] > tamanhoTela[1] + 50 and obj["tipo"] != "bomba":
                    obj["ativo"] = False
                    vidas -= 1

                tela.blit(obj["imagem"], (obj["x"], obj["y"]))

        # --- Capturar movimento do mouse (arrasto) ---
        pos_mouse = pygame.mouse.get_pos()
        mouse_trilha.append(pos_mouse)
        if len(mouse_trilha) > 10:
            mouse_trilha.pop(0)

        # Desenhar trilha vermelha (efeito do corte)
        if len(mouse_trilha) > 1:
            pygame.draw.lines(tela, VERMELHO, False, mouse_trilha, 3)

        # --- Detectar corte ---
        if pygame.mouse.get_pressed()[0]:  # botão esquerdo pressionado
            for obj in objetos:
                if obj["ativo"]:
                    rect = obj["imagem"].get_rect(topleft=(obj["x"], obj["y"]))
                    x_rel = int(pos_mouse[0] - obj["x"])
                    y_rel = int(pos_mouse[1] - obj["y"])
                    if 0 <= x_rel < rect.width and 0 <= y_rel < rect.height:
                        if obj["mascara"].get_at((x_rel, y_rel)):
                            obj["ativo"] = False
                            if obj["tipo"] == "bomba":
                                vidas = 0
                            elif obj["tipo"] == "pimenta":
                                placar += 5
                            else:
                                placar += 1
                            pygame.draw.circle(tela, VERDE, pos_mouse, 40, 3)

        # --- Remover objetos inativos ---
        objetos = [obj for obj in objetos if obj["ativo"]]

        # --- Mostrar placar e vidas ---
        desenhar_texto(f"Pontuação: {placar}", (10, 10))
        desenhar_texto(f"Vidas: {vidas}", (tamanhoTela[0] - 150, 10))

        # --- Verificar fim de jogo ---
        if vidas <= 0:
            tela.fill(PRETO)
            ranking = open("rankinglog.txt","a+", encoding="utf-8")
            ranking.seek(0) 
            if ranking.read().strip() == "":
                ranking.write(f"{str(placar)}\n")
            else:
                ranking.seek(0)  
                log = ranking.readlines()
                # converter linhas para inteiros
                pontuacoes = [int(n.strip()) for n in log if n.strip()]
                # adicionar placar apenas se for maior que qualquer pontuação existente
                if placar > max(pontuacoes):
                    ranking.write(f"{placar}\n")
            ranking.close()
            desenhar_texto("GAME OVER", (tamanhoTela[0] // 2 - 120, tamanhoTela[1] // 2 - 40), VERMELHO)
            desenhar_texto(f"Pontuação final: {placar}", (tamanhoTela[0] // 2 - 140, tamanhoTela[1] // 2 + 20))
            desenhar_texto("Pressione R para reiniciar", (tamanhoTela[0] // 2 - 200, tamanhoTela[1] // 2 + 80))
            pygame.display.update()

            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        placar = 0
                        vidas = 3
                        objetos.clear()
                        ultimo_lancamento = pygame.time.get_ticks()
                        esperando = False
                clock.tick(30)

    pygame.display.update()
    clock.tick(60)
