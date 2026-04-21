import pyttsx3
import pygame
import argparse
import threading
import time
import re
import os

# ---------------------------
# TTS (fala contínua)
# ---------------------------
class TTSWorker(threading.Thread):
    def __init__(self, texto, wpm):
        super().__init__()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', wpm)
        self.texto = texto
        self.running = True
        self.paused = False

    def run(self):
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            self.engine.say(self.texto)
            self.engine.runAndWait()
            break  # fala uma vez só

    def stop(self):
        self.running = False
        self.engine.stop()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.engine.stop()
        else:
            # reinicia leitura do zero (limitação do pyttsx3)
            self.engine.say(self.texto)

# ---------------------------
# RSVP display
# ---------------------------
def desenhar_palavra(screen, font, palavra):
    screen.fill((0, 0, 0))

    if not palavra:
        return

    meio = len(palavra) // 2

    prefixo = palavra[:meio]
    letra = palavra[meio]
    sufixo = palavra[meio+1:]

    cor_normal = (200, 200, 200)
    cor_destaque = (255, 80, 80)

    surf_prefixo = font.render(prefixo, True, cor_normal)
    surf_letra = font.render(letra, True, cor_destaque)
    surf_sufixo = font.render(sufixo, True, cor_normal)

    largura_total = (
        surf_prefixo.get_width() +
        surf_letra.get_width() +
        surf_sufixo.get_width()
    )

    x = (screen.get_width() - largura_total) // 2
    y = screen.get_height() // 2

    screen.blit(surf_prefixo, (x, y))
    x += surf_prefixo.get_width()

    screen.blit(surf_letra, (x, y))
    x += surf_letra.get_width()

    screen.blit(surf_sufixo, (x, y))

# ---------------------------
# MAIN
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo")
    parser.add_argument("--vel", type=int, default=300)
    args = parser.parse_args()

    if not os.path.exists(args.arquivo):
        print("Arquivo não encontrado")
        return

    with open(args.arquivo, "r", encoding="utf-8") as f:
        texto = f.read()

    palavras = re.findall(r'\S+', texto)

    delay = 60.0 / args.vel

    # inicia TTS com TEXTO INTEIRO
    tts = TTSWorker(texto, args.vel)
    tts.start()

    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("RSVP Reader")

    font = pygame.font.SysFont("Arial", 64)
    clock = pygame.time.Clock()

    index = 0
    paused = False
    last_update = time.time()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    tts.toggle_pause()

                elif event.key == pygame.K_RIGHT:
                    index = min(index + 1, len(palavras) - 1)

                elif event.key == pygame.K_LEFT:
                    index = max(index - 1, 0)

        if not paused:
            if time.time() - last_update >= delay:
                index += 1
                last_update = time.time()

        if index < len(palavras):
            desenhar_palavra(screen, font, palavras[index])

        pygame.display.flip()
        clock.tick(60)

    tts.stop()
    pygame.quit()

if __name__ == "__main__":
    main()