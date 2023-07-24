import os
import sys
import time
import logging
import msvcrt
from Entities.Node import Node

class Game:
    COMMANDS = ["/help", "/inventory", "/exit"]

    def __init__(self, name, current_node, inventory, node_history, choice_history):
        self.continue_loop = True
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
        print()
        remaining_text = text

        for char in text:
            if msvcrt.kbhit() and msvcrt.getch() == b' ': # Only works in Windows
                for line in remaining_text.split("\\"):
                    print(line.strip())
                return

            if char == "\\":
                print()
            else:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.01)

            remaining_text = remaining_text[1:]
        print()

    def display_inventory(self):
        print("[INVENTORY]")
        if not self.inventory:
            print("Empty")
        else:
            for item in self.inventory:
                print(item)

    def run_command(self, command):
        if command == "/inventory":
            self.display_inventory()
        elif command == "/exit":
            self.continue_loop = False
        elif command == "/help":
            print("[COMMANDS]")
            for command in Game.COMMANDS:
                print(command)
        else:
            print("Invalid command. Try \"/help\" for the list of commands")

    def display_description(self):
        description = self.current_node.revisited_description if self.current_node.id in self.node_history else self.current_node.description

        if description:
            Game.print_delay(description)

    def display_choices(self):       
        choices_to_display=[]
        for choice in self.current_node.choices:
            if not self.check_choice_requirements(choice.visibility_requirement):             
                continue
            elif choice.consequence and choice.consequence.remove_choice and choice.true_node.id in self.node_history:
                continue
            else:
                choices_to_display.append(choice)

        print() 
        for choice in choices_to_display:
            print(f"[{choice.name.upper()}] ", end='')
        print()

    def get_input(self):
        while True:
            choice_input = input('\n').lower().strip()
            if choice_input.startswith("/"):
                self.run_command(choice_input)
                if not self.continue_loop:
                    return
            else:
                for choice in self.current_node.choices:
                    if choice_input == choice.name.lower():
                        self.selected_choice = choice
                        return
                print("Invalid choice. Please try again.")

    def check_choice_requirements(self,requirement):
        if not requirement:
            return True

        has_items = self.check_requirement(requirement.items, self.inventory)
        visited_nodes = self.check_requirement(requirement.node_visits, self.node_history)
        made_choices = self.check_requirement(requirement.choices, self.choice_history)

        return has_items and visited_nodes and made_choices

    def check_requirement(self, requirement_list, player_list):
        if not requirement_list:
            return True

        for item in requirement_list:
            if item not in player_list:
                return False
        return True

    def apply_consequence(self):
        if self.selected_choice.consequence is None:
            return

        for item in self.selected_choice.consequence.items:
            if item.startswith('-'):
                self.inventory.remove(item[1:])
            elif item.startswith('+'):
                self.inventory.append(item[1:])

    def move_to_new_node(self, next_node):
        if not self.current_node.id in self.node_history:
            self.node_history.append(self.current_node.id)

        if self.selected_choice and not self.selected_choice.id in self.choice_history:
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

        if isinstance(node, Node):
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
                self.get_input()

                if not self.continue_loop:
                    return

                Game.clear()
                if self.selected_choice.navigation_requirement and not self.check_choice_requirements(self.selected_choice.navigation_requirement):
                    next_node = self.selected_choice.false_node
                else:
                    self.apply_consequence()
                    next_node = self.selected_choice.true_node

            self.move_to_new_node(next_node)