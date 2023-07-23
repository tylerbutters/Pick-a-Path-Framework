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
    #    Main.game = Game("", Main.nodes.get("<START>"), [], [], [] )
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
        option = input('\n').lower().strip()
        
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
            Main.clear()
            Main.print_title("select save")
            print("[BACK] [DELETE]")
            for save in Main.save_files.values():
                print(f"[NAME: {save.name.upper()}]")
            while True:
                save_name = input().lower().strip()
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
            while True:
                save_name = input().lower().strip()
                if save_name == "back":               
                    return    
                elif save_name in Main.save_files:
                    Main.save_files.pop(save_name)
                    FileManager.write_saves(Main.save_files.values())
                    break;
                else:
                    print("Invalid choice. Please try again.")
            
    @staticmethod
    def make_new_game():
        Main.clear()
        Main.print_title("new game")
        print("Enter name: ", end="")
        name = input().lower().strip()       
        print(f"\nConfirm \"{name}\"?\n\n[YES] [NO]")
        while True:
            confirm = input().lower().strip()
            if confirm == "yes":
                Main.game = Game(name, copy.deepcopy(Main.nodes.get("<START>")), [], [], [])
                return
            elif confirm == "no":
                return
            else:
                print("Invalid choice. Please try again.")
    
    @staticmethod
    def save_game():
        node = Main.game.current_node
        Main.game.current_node = Main.game.current_node.id  # Save the current_node.id to a variable
        Main.save_files[Main.game.name] = Main.game
        FileManager.write_saves(Main.save_files.values())
        Main.game.current_node = node  # Restore the current_node to its original object


    @staticmethod
    def start_game():
        Main.clear()
        Main.save_game()
        while Main.game.continue_loop:
            Main.game.game_loop()
            Main.save_game()

if __name__ == "__main__":
    Main.main()