from Game import Game
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    game = Game()
    
    while True:
        game.game_loop()

main()