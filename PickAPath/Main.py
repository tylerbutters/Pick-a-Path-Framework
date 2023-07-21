from sys import displayhook
from FileManager import FileManager
from Game import Game
import logging
import os
import copy

logging.basicConfig(level=logging.DEBUG)

class Main:   
    nodes = {}
    save_files = {}
    main_options = ["new","load","exit"]
    game = None

    @staticmethod
    def clear():
        pass
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_title(text):
        line = "----------------"
        print(line)
        print(text.upper())
        print(line,'\n')

    @staticmethod
    def main():      
        Main.nodes = FileManager.load_all_nodes()
        while True:
            Main.save_files = FileManager.read_save_files() # dict of game objects with string ids
            Main.display_main_menu()
            Main.select_option()
            if type(Main.game) is Game:
                Main.start_game()
            else:
                logging.error("no game object")
    
    #@staticmethod
    #def main():
    #    Main.save_files = FileManager.read_save_files()
    #    Main.nodes = FileManager.load_all_nodes()
    #    Main.game = Game(Main.nodes, "", Main.nodes.get("N1"), [], [], [] )
    #    Main.start_game()

    @staticmethod
    def display_main_menu():
        Main.clear()
        Main.print_title("main menu")
        for option in Main.main_options:
            if option == "load" and not Main.save_files:
                continue
            print(f"[{option.upper()}] ", end='')
    
    @staticmethod
    def select_option():
        option = input('\n').lower()
        
        if option == "exit":
            raise SystemExit
        elif option == "load":
            Main.choose_save_file()           
        elif option == "new":
            Main.make_new_game()
        else:
            print("Invalid choice. Please try again.")

    @staticmethod
    def choose_save_file():
        while True:
            Main.display_save_files()
            Main.select_save()
            if Main.game:
                return

    @staticmethod
    def display_save_files():
        Main.clear()
        Main.print_title("select save")
        print("[BACK] [DELETE]")
        for save in Main.save_files.values():
            print(f"[NAME: {save.name.upper()}]")       

    @staticmethod
    def select_save():
        while True:
            save_name = input().lower()
            if save_name == "back":
                return
            elif save_name == "delete":
                Main.delete_save_file()
                return
            save = Main.save_files.get(save_name)
            if save:
                if not save.current_node or type(save) is not Game:
                    logging.error("save has no node object")
                    continue
                save.current_node = copy.deepcopy(Main.nodes.get(save.current_node))
                Main.game = save               
                return
            else:
                print("Invalid choice. Please try again.")

    @staticmethod
    def delete_save_file():
        while True:
            Main.clear()
            Main.print_title("select save to delete")
            print("[BACK]")
            for save in Main.save_files.values():
                print(f"[NAME: {save.name.upper()}]") 

            save_name = input()
            if save_name == "back":               
                return    
            elif save_name in Main.save_files:
                Main.save_files.pop(save_name)
                FileManager.write_saves(Main.save_files.values())
            else:
                print("Invalid choice. Please try again.")
            
    @staticmethod
    def make_new_game():
        Main.clear()
        Main.print_title("new game")
        print("Enter name: ", end="")
        name = input()
        while True:
            print(f"\nConfirm \"{name}\"?\n\n[YES] [NO]")

            confirm = input().lower()
            if confirm == "yes":
                Main.game = Game(name, copy.deepcopy(Main.nodes.get("N1")), [], [], [])

                return
            elif confirm == "no":
                return
            else:
                print("Invalid choice. Please try again.")
    
    @staticmethod
    def save_game():
        Main.game.current_node = Main.game.current_node.id # turn object to string
        Main.save_files[Main.game.name] = Main.game
        FileManager.write_saves(Main.save_files.values())

    @staticmethod
    def start_game():
        Main.clear()
        while Main.game.continue_loop:
            Main.game.game_loop()
            if Main.game.save_pending:
                Main.save_game()
        Main.save_game()

if __name__ == "__main__":
    Main.main()