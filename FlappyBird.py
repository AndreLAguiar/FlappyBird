import pygame
import os
import random
import neat


ai_jogando = True
recorde, geracao, recorde_geracao = 0,0,0


TELA_LARGURA = 600
TELA_ALTURA = 770

original_bird1 = pygame.image.load(os.path.join('img', 'bird-1.png'))
bird1_width, bird1_height = original_bird1.get_size()
new_width_bird1 = bird1_width // 2.3
new_height_bird1 = bird1_height // 2.3
bird_1 = pygame.transform.scale(original_bird1, (new_width_bird1, new_height_bird1))

original_bird2 = pygame.image.load(os.path.join('img', 'bird-2.png'))
bird2_width, bird2_height = original_bird2.get_size()
new_width_bird2 = bird2_width // 2.3
new_height_bird2 = bird2_height // 2.3
bird_2 = pygame.transform.scale(original_bird2, (new_width_bird2, new_height_bird2))

original_bird3 = pygame.image.load(os.path.join('img', 'bird-3.png'))
bird3_width, bird3_height = original_bird3.get_size()
new_width_bird3 = bird3_width // 2.3
new_height_bird3 = bird3_height // 2.3
bird_3 = pygame.transform.scale(original_bird3, (new_width_bird3, new_height_bird3))

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'chao.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'background.png')))
IMAGEM_PASSARO = [bird_1, bird_2, bird_3]

pygame.font.init()
FONT_PONTOS = pygame.font.SysFont('arial', 35)
FONT_MELHOR_PONTO = pygame.font.SysFont('arial', 25)


class Passaro:
    IMGS = IMAGEM_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 25
    TEMPO_ANIMACAO = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo
        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
            
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]


        # se o passaro estiver caindo não vai bater a asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem,  self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)   

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    VELOCIDADE = 6
    velocidade_sobe_desce = 2
    troca_posicao_tempo = 1000
    ultima_troca = pygame.time.get_ticks()
    indo_pracima = True

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.CANO = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(-182, 0)
        self.pos_topo = self.altura
        self.pos_base = self.altura + self.CANO.get_height()-160
        
    def mover(self):
        self.x -= self.VELOCIDADE

        # Verificando se é hora de mudar de direção
        tempo = pygame.time.get_ticks()
        if tempo - self.ultima_troca > self.troca_posicao_tempo:
            self.ultima_troca = tempo
            self.indo_pracima = not self.indo_pracima

        # Movendo a imagem para cima ou para baixo
        if self.indo_pracima:
            self.pos_topo -= self.velocidade_sobe_desce
        else:
            self.pos_topo += self.velocidade_sobe_desce

        # Verificando se a imagem não sai da tela
        if self.altura < -150:
            self.altura = -150
            self.indo_pracima = False
        if self.altura > -80:
            self.altura = -80
            self.indo_pracima = True



    def desenhar(self, tela):
        tela.blit(self.CANO, (self.x, self.pos_topo))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        cano_mask = pygame.mask.from_surface(self.CANO)

        distancia_cano = (self.x - passaro.x, self.pos_topo - round(passaro.y))

        cano_ponto = passaro_mask.overlap(cano_mask, distancia_cano)

        if cano_ponto:
            return True
        else:
            return False
        
class Chao:
    VELOCIDADE = 6
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos, recorde, qtd_passaro):
    
    tela.blit(IMAGEM_BACKGROUND, (0, -200))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
              
    if ai_jogando:
        texto_passaros = FONT_MELHOR_PONTO.render(f'Qtde passaros: {qtd_passaro}', 1, (255, 255, 255))
        tela.blit(texto_passaros, (25, 50))
        texto_geracao = FONT_PONTOS.render(f'Geração: {geracao}', 1, (255, 255, 255))
        tela.blit(texto_geracao, (25, 10))

    texto_pontos = FONT_PONTOS.render(f'Pontuação: {pontos}', 1, (255, 255, 255))
    tela.blit(texto_pontos, (TELA_LARGURA - 10 - texto_pontos.get_width(), 10))

    texto_record = FONT_MELHOR_PONTO.render(f'Recorde: {recorde} - Ger.{recorde_geracao}', 1, (255, 255, 255))
    tela.blit(texto_record, (TELA_LARGURA - 10 - texto_record.get_width(), 50))


    chao.desenhar(tela)
    pygame.display.update()


def main(genomas, config):
    global geracao, recorde, recorde_geracao
    geracao += 1
                
    if ai_jogando:
        redes = []
        lista_genomas = []
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            passaros.append(Passaro(200, 350))
    else:
        passaros = [Passaro(180, 350)]

    chao = Chao(700)
    canos = [Cano(600)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()
    qtd_passaro = 0
    
    rodando = True
    while rodando:
        relogio.tick(30)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].CANO.get_width()):
                indice_cano = 1
            qtd_passaro = len(passaros)
        else:
            rodando = False
            break

        for i, passaro in enumerate(passaros):
            passaro.mover()
            if ai_jogando:
                lista_genomas[i].fitness += 0.1
                output = redes[i].activate((passaro.y, 
                                            abs(passaro.y - canos[indice_cano].altura),
                                            abs(passaro.y - canos[indice_cano].pos_base)))
                if output[0] > 0.5:
                    passaro.pular() 

        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not cano.passou and cano.x < 50:
                    cano.passou = True
                    adicionar_cano = True
                    pontos += 1                    
                    if recorde < pontos:
                        recorde = pontos
                        recorde_geracao = geracao
                                             
            cano.mover()
            if cano.x + cano.CANO.get_width() < -40:
                remover_canos.append(cano)

        if adicionar_cano:
            canos.append(Cano(600))
            if ai_jogando:
                for genoma in lista_genomas:
                    genoma.fitness += 5
        for cano in remover_canos:
            canos.remove(cano)
            
        for i, passaro in enumerate(passaros):
            if(passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ai_jogando:
                    lista_genomas.pop(i)
                    redes.pop(i)

                
        desenhar_tela(tela, passaros, canos, chao, pontos, recorde, qtd_passaro)

        
def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())

    if ai_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)
