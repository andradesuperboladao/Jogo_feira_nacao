import pygame
import random
import math
from PIL import Image, ImageSequence
from pygame.locals import *
from sys import exit

pygame.init()
pygame.font.init()

# --- CONFIGURAÇÕES BÁSICAS ---
musica_fundo = pygame.mixer.Sound("audio/musica.mp3")
musica_fundorapida = pygame.mixer.Sound("audio/musicarapida.mp3")
barulhoBomba = pygame.mixer.Sound("audio/bomba.wav")
barulhoCorte = pygame.mixer.Sound("audio/corte.wav")
tamanhoTela = pygame.display.get_desktop_sizes()[0] 
largura, altura = tamanhoTela
tela = pygame.display.set_mode(tamanhoTela)
pygame.display.set_caption("Burrito Blade")
pygame.mixer.Sound.play(musica_fundo, loops=-1)

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
ROXO = (102,51,153)

fonte = pygame.font.SysFont('Sans-serif', 36)
clock = pygame.time.Clock()

# --- FUNÇÕES AUXILIARES ---
def carregar_gif_frames(caminho, tamanho=(200, 200)):
    frames = []
    gif = Image.open(caminho)
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        frame = frame.resize(tamanho)
        modo, size, data = frame.mode, frame.size, frame.tobytes()
        py_image = pygame.image.fromstring(data, size, modo)
        frames.append(py_image)
    return frames

def carregar_ranking():
    ranking = []
    try:
        with open("rankinglog.txt", "r", encoding="utf-8") as log:
            for linha in log:
                if ":" in linha:
                    nome, pontos = linha.strip().split(":")
                    ranking.append((nome, int(pontos)))
    except FileNotFoundError:
        pass

    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking[:5]

def desenhar_menu():
    tela.fill(PRETO)

    titulo = fonte.render("MEXICO NINJA", True, BRANCO)
    jogar = fonte.render("JOGAR", True, BRANCO)
    credito = fonte.render("By NATADO2AI", True, BRANCO)

    tela.blit(titulo, (largura//2 - titulo.get_width()//2, 80))

    y = 180
    texto_top = fonte.render("===== HIGHSCORES =====", True, ROXO)
    tela.blit(texto_top, (largura//2 - texto_top.get_width()//2, y))
    y += 40

    for i, (nome, pontos) in enumerate(top5, start=1):
        txt = fonte.render(f"{i}. {nome} - {pontos}", True, BRANCO)
        tela.blit(txt, (largura//2 - txt.get_width()//2, y))
        y += 40

    texto_bottom = fonte.render("=======================", True, ROXO)
    tela.blit(texto_bottom, (largura//2 - texto_bottom.get_width()//2, y))

    botao = pygame.Rect(largura//2 - 100, altura//2 + 120, 200, 60)
    pygame.draw.rect(tela, BRANCO, botao, 2)
    tela.blit(jogar, (largura//2 - jogar.get_width()//2, altura//2 + 120 + (60 - jogar.get_height())//2))

    tela.blit(credito, (largura//2 - credito.get_width()//2, altura - 50))

    caveira_original_menu = pygame.image.load("img/caveira.png").convert()
    caveira_menu = pygame.transform.scale(caveira_original_menu, (200, 200))
    tela.blit(caveira_menu, (-20, 25))
    tela.blit(caveira_menu, (largura - caveira_menu.get_width(), 25))

    return botao

def lancar_objeto():
    tipo = random.choice(["burrito", "taco", "pimenta", "bomba", "chapeu"])
    if tipo == "burrito":
        imagem = burrito_img
    elif tipo == "taco":
        imagem = taco_img
    elif tipo == "pimenta":
        imagem = pimenta_img
    elif tipo == "chapeu":
        imagem = chapeu_img
    else:
        imagem = bomba_img

    imagem = pygame.transform.scale(imagem, (200, 200))
    mascara = pygame.mask.from_surface(imagem)

    obj_larg = imagem.get_width()
    x = random.randint(obj_larg // 2, largura - obj_larg // 2)
    y = altura + 50
    velocidade_x = random.uniform(-4, 4)
    velocidade_y = random.uniform(-30, -22)
    gravidade = 0.5

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

def pedir_nome():
    nome = ""
    pedindo = True
    while pedindo:
        tela.fill(PRETO)
        texto = fonte.render("Digite seu nome:", True, BRANCO)
        nome_render = fonte.render(nome, True, VERDE)
        instrucao = fonte.render("Pressione ENTER para confirmar", True, BRANCO)
        
        tela.blit(texto, (largura//2 - texto.get_width()//2, altura//2 - 100))
        tela.blit(nome_render, (largura//2 - nome_render.get_width()//2, altura//2))
        tela.blit(instrucao, (largura//2 - instrucao.get_width()//2, altura//2 + 60))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and nome.strip():
                    pedindo = False
                elif event.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    if len(nome) < 15 and event.unicode.isprintable():
                        nome += event.unicode
    return nome

# --- VARIÁVEIS DE JOGO ---
estado = "menu"
placar = 0
vidas = 3
objetos = []
ultimo_lancamento = 0
intervalo_lancamento = 800
mouse_trilha = []
bomba_explodiu = False
tempo_explosao = 0
game_over_delay = 0
top5 = carregar_ranking()
mostrar_efeito_pimenta = False
canal_musica = pygame.mixer.Channel(0)

# --- NOVAS VARIÁVEIS DE VELOCIDADE ---
velocidade_base = 1.0          # aceleração permanente (por pontuação)
velocidade_pimenta = 1.0       # aceleração temporária (por pimenta)
tempo_pimenta_ativa = 0
duracao_pimenta = 4000         # duração do efeito da pimenta (ms)

# --- CARREGAR IMAGENS e ANIMAÇÕES ---
chapeu_img = pygame.image.load("img/chapeu.png")
burrito_img = pygame.image.load("img/burrito.png")
bomba_img = pygame.image.load("img/caveira.png")
taco_img = pygame.image.load("img/taco.png")
pimenta_img = pygame.image.load("img/pimenta.png")
anim_pimenta = carregar_gif_frames("img/cortepimenta.gif")
anim_chapeu = carregar_gif_frames("img/cortechapeu.gif")
anim_bomba = carregar_gif_frames("img/cortebomba.gif")
anim_burrito = carregar_gif_frames("img/corteburrito.gif")
anim_taco = carregar_gif_frames("img/cortetaco.gif")

# --- FUNDO ---
fundo_img = pygame.image.load("img/fundojogo.png")
fundo_img = pygame.transform.scale(fundo_img, tamanhoTela)

# --- LOOP PRINCIPAL ---
rodando = True
while rodando:
    if estado == "menu":
        pygame.mixer.Sound.stop(musica_fundo)
        top5 = carregar_ranking()
        botao_jogar = desenhar_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(event.pos):
                    canal_musica.play(musica_fundo, loops=-1)
                    estado = "jogo"
                    placar = 0
                    vidas = 3
                    objetos.clear()
                    ultimo_lancamento = pygame.time.get_ticks()
                    bomba_explodiu = False
                    velocidade_base = 1.0
                    velocidade_pimenta = 1.0

    elif estado == "jogo":
        
        tela.blit(fundo_img, (0, 0))
        teclas = pygame.key.get_pressed()
        tempo_atual = pygame.time.get_ticks()

        if mostrar_efeito_pimenta:
            tempo_passado = tempo_atual - tempo_pimenta_ativa
            if tempo_passado < duracao_pimenta:
                intensidade = 255 - int((tempo_passado / duracao_pimenta) * 200)
                cor = (255, intensidade // 2, intensidade // 2)  # vermelho decrescente
                overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
                pygame.draw.rect(overlay, (*cor, 80), overlay.get_rect(), 40)  # bordas vermelhas transparentes
                tela.blit(overlay, (0, 0))
                if canal_musica.get_sound() != musica_fundorapida:
                    canal_musica.stop()
                    canal_musica.play(musica_fundorapida, loops=-1)
            else:
            # efeito terminou
                mostrar_efeito_pimenta = False
                # volta à música normal
                if canal_musica.get_sound() != musica_fundo:
                    canal_musica.stop()
                    canal_musica.play(musica_fundo, loops=-1)
        else:
        # música normal (se não estiver tocando)
            if canal_musica.get_sound() != musica_fundo:
                canal_musica.stop()
                canal_musica.play(musica_fundo, loops=-1)

        # --- AJUSTE DE VELOCIDADE ---
        velocidade_base = 1.0 + (placar // 100.0)  # a cada 100 pontos dobra a velocidade

        if tempo_pimenta_ativa > 0:
            if tempo_atual - tempo_pimenta_ativa > duracao_pimenta:
                velocidade_pimenta = 1.0
                tempo_pimenta_ativa = 0

        multiplicador_geral = velocidade_base * velocidade_pimenta

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if teclas[pygame.K_x]:
                rodando = False


        intervalo_real = intervalo_lancamento / multiplicador_geral

        if tempo_atual - ultimo_lancamento > intervalo_real:
            lancar_objeto()
            ultimo_lancamento = tempo_atual
            intervalo_lancamento = random.randint(600, 1200)

        for obj in objetos:
            if obj.get("ativo", False):
                if "vel_x" in obj:
                    obj["x"] += obj["vel_x"] * multiplicador_geral
                    obj["y"] += obj["vel_y"] * multiplicador_geral
                    obj["vel_y"] += obj["grav"] * multiplicador_geral

                    if obj["x"] < 0:
                        obj["x"] = 0
                        obj["vel_x"] *= -0.8
                    elif obj["x"] + obj["imagem"].get_width() > largura:
                        obj["x"] = largura - obj["imagem"].get_width()
                        obj["vel_x"] *= -0.8

                    if obj["y"] > tamanhoTela[1] + 50 and obj["tipo"] != "bomba":
                        obj["ativo"] = False
                        vidas -= 1

                if obj["tipo"] != "animacao":
                    tela.blit(obj["imagem"], (obj["x"], obj["y"]))
                else:
                    tempo = pygame.time.get_ticks()
                    if tempo - obj["timer"] > obj["frame_delay"]:
                        obj["timer"] = tempo
                        obj["frame_atual"] += 1
                        if obj["frame_atual"] >= len(obj["frames"]):
                            obj["ativo"] = False
                            continue
                    tela.blit(obj["frames"][obj["frame_atual"]], (obj["x"], obj["y"]))

        pos_mouse = pygame.mouse.get_pos()
        mouse_trilha.append(pos_mouse)
        if len(mouse_trilha) > 10:
            mouse_trilha.pop(0)

        if len(mouse_trilha) > 1:
            pygame.draw.lines(tela, VERMELHO, False, mouse_trilha, 3)

        if pygame.mouse.get_pressed()[0]:
            for obj in objetos:
                if obj.get("ativo", False) and obj["tipo"] != "animacao":
                    rect = obj["imagem"].get_rect(topleft=(obj["x"], obj["y"]))
                    x_rel = int(pos_mouse[0] - obj["x"])
                    y_rel = int(pos_mouse[1] - obj["y"])
                    if 0 <= x_rel < rect.width and 0 <= y_rel < rect.height:
                        if obj["mascara"].get_at((x_rel, y_rel)):
                            obj["ativo"] = False
                            anim_frames = None

                            if obj["tipo"] == "bomba":
                                anim_frames = anim_bomba
                                bomba_explodiu = True
                                tempo_explosao = pygame.time.get_ticks()
                                game_over_delay = 500
                            elif obj["tipo"] == "pimenta":
                                anim_frames = anim_pimenta
                                placar += 5
                                velocidade_pimenta = 1.35  # acelera temporariamente
                                tempo_pimenta_ativa = pygame.time.get_ticks()
                                mostrar_efeito_pimenta = True
                            elif obj["tipo"] == "burrito":
                                anim_frames = anim_burrito
                                placar += 1
                            elif obj["tipo"] == "taco":
                                anim_frames = anim_taco
                                placar += 1
                            elif obj["tipo"] == "chapeu":
                                anim_frames = anim_chapeu
                                placar += 2

                            if anim_frames:
                                anim_obj = {
                                    "tipo": "animacao",
                                    "frames": anim_frames,
                                    "frame_atual": 0,
                                    "x": obj["x"],
                                    "y": obj["y"],
                                    "timer": pygame.time.get_ticks(),
                                    "frame_delay": 50,
                                    "ativo": True
                                }
                                objetos.append(anim_obj)
                                barulhoCorte.play()
                            if obj["tipo"] == "bomba":
                                barulhoBomba.play()
                            

        objetos = [obj for obj in objetos if obj.get("ativo", False)]

        desenhar_texto(f"Pontuação: {placar}", (10, 10))
        desenhar_texto(f"Vidas: {vidas}", (tamanhoTela[0] - 150, 10))

        if bomba_explodiu and pygame.time.get_ticks() - tempo_explosao >= game_over_delay:
            vidas = 0

        if vidas <= 0:
            canal_musica.stop()
            tela.fill(PRETO)
            nome_jogador = pedir_nome()
            tela.fill(PRETO)
            with open("rankinglog.txt", "a+", encoding="utf-8") as ranking:
                ranking.write(f"{nome_jogador}:{placar}\n")

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
                        bomba_explodiu = False
                        velocidade_base = 1.0
                        velocidade_pimenta = 1.0
                        estado = "menu"
                        esperando = False
                clock.tick(30)
        

    pygame.display.update()
    clock.tick(60)