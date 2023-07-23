import logging
import time
import sys
import os
from Node import Node

class Game:
    commands = ["/help","/inventory","/exit","/save"]

    def __init__(self, name, current_node, inventory, node_history, choice_history):
        self.continue_loop = True
        self.save_pending = False
        self.name = name
        self.current_node = current_node  
        self.selected_choice = None
        self.inventory = inventory   
        self.node_history = node_history
        self.choice_history = choice_history   

    @staticmethod
    def clear():
        pass
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_delay(text):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)
        print()

    def display_inventory(self):
        print("[INVENTORY]")
        if not self.inventory:
            print("Empty")
        else:
            print(self.inventory)

    def run_command(self,command):
        if command == "/inventory":
            self.display_inventory()
        elif command == "/exit":
            self.continue_loop = False
        elif command == "/help":
            print("[COMMANDS]")
            [print(command) for command in Game.commands]

    def display_description(self):
        print()
        description = self.current_node.revisited_description if self.current_node.id in self.node_history else self.current_node.description
        lines = description.split("\\")
        for line in lines:
            Game.print_delay(line.strip())       

    def display_choices(self):
        print()
        choices = list(self.current_node.choices)
        for choice in choices:
            if choice.consequence and choice.consequence.remove_choice and choice.id in self.choice_history:
                self.current_node.choices.remove(choice)
                continue
            print(f"[{choice.name.upper()}] ", end='')
        print()
    
    def select_choice(self):
        while True:
            choice_input = input('\n').lower().strip()  # Strip any leading/trailing spaces
            if choice_input.startswith("/"):
                self.run_command(choice_input)
                if not self.continue_loop:
                    return
                else:
                    continue

            for choice in self.current_node.choices:
                if choice_input == choice.name.lower():
                    self.selected_choice = choice
                    return

            print("Invalid choice. Please try again.")

    def check_choice_requirements(self):
        if self.selected_choice.requirement is None:
            return True

        requirement = self.selected_choice.requirement   

        has_items = self.check_requirement(requirement.items, self.inventory)
        visited_nodes = self.check_requirement(requirement.node_visits, self.node_history)
        made_choices = self.check_requirement(requirement.choices, self.choice_history)

        return has_items and visited_nodes and made_choices

    def check_requirement(self, requirement_list, player_list):
        return all(item in player_list for item in requirement_list)

    def apply_consequence(self):
        if self.selected_choice.consequence is None:
            return

        for item in self.selected_choice.consequence.items:
            if item.startswith('-'):
                self.inventory.remove(item[1:])
            elif item.startswith('+'):
                self.inventory.append(item[1:])

    def move_to_new_node(self,next_node):
        self.node_history.append(self.current_node.id)

        if self.selected_choice:
            self.choice_history.append(self.selected_choice.id)

        self.selected_choice = None
        self.current_node = next_node
    
    def end_game(self):
        self.display_description()
        print("\n[THE END]\n[EXIT]")
        while True:
            end_input = input().lower().strip()
            if end_input == "exit":
                return
            else:
                print("Invalid choice. Please try again.")

    def check_node(self):
        node = self.current_node

        if node and type(node) is Node:
            if node.choices or node.target_node:
                return True
            elif node.id == "<END>":
                self.end_game()
        else:
            logging.error(f"Node is invalid: {self.current_node}")
            
        self.continue_loop = False
        return False
            
    def game_loop(self):
        if self.check_node():
            self.display_description()

            if self.current_node.target_node:  # continuation or rebound node
                next_node = self.current_node.target_node

            elif self.current_node.choices:  # branch node
                self.display_choices()
                self.select_choice()

                if not self.continue_loop:
                    return

                Game.clear()
                if self.selected_choice.requirement and not self.check_choice_requirements():
                    next_node = self.selected_choice.false_node
                else:
                    self.apply_consequence()
                    next_node = self.selected_choice.true_node

            self.move_to_new_node(next_node)
        
