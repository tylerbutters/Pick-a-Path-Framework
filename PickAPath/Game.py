import logging
import time
import sys
import os


class Game:
    nodes = {}
    commands = ["/help","/inventory","/exit","/save"]

    def __init__(self, nodes, name, current_node, previous_node, previous_selected_choice, inventory, node_history, choice_history):
        Game.nodes = nodes
        self.continue_loop = True
        self.save_pending = False
        self.name = name
        self.current_node = current_node
        self.previous_node = previous_node   
        self.selected_choice = None
        self.previous_selected_choice = previous_selected_choice
        self.inventory = inventory   
        self.node_history = node_history
        self.choice_history = choice_history 

    def display_inventory(self):
        print("[INVENTORY]")
        if not self.inventory:
            print("Empty")
            return
        print(self.inventory)

    @staticmethod
    def clear():
        pass
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_delay(text):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.00)
        print()

    def run_command(self,command):
        if command == "/inventory":
            self.display_inventory()
        elif command == "/save":
            print("GAME SAVED!")
            self.save_pending = True
        elif command == "/help":
            print("[COMMANDS]")
            [print(command) for command in Game.commands]


    def check_node(self):
        if not self.current_node:
            logging.error(f"Node is invalid: {self.current_node}")
            self.continue_loop = False

    def display_description(self):
        print()
        description = self.current_node.revisited_description if self.current_node.is_visited else self.current_node.description
        lines = description.split("\\")
        for line in lines:
            Game.print_delay(line.strip())       

    def display_choices(self):
        print()
        print(''.join(f"[{choice.name.upper()}] " for choice in self.current_node.choices))
        print()
    
    def select_choice(self):
        while True:
            choice_input = input('\n').strip().lower()  # Strip any leading/trailing spaces
            if choice_input.startswith("/"):
                if choice_input == "/exit":
                    self.continue_loop = False
                    return
                self.run_command(choice_input)
                continue

            for choice in self.current_node.choices:
                if choice_input.lower() == choice.name.lower():
                    self.selected_choice = choice
                    return

            print("Invalid choice. Please try again.")

    def check_choice_requirements(self):       
        requirement = self.selected_choice.requirement

        if requirement is None:
            return True

        has_items = self.check_requirement(requirement.items, self.inventory)
        visited_nodes = self.check_requirement(requirement.node_visits, self.node_history)
        made_choices = self.check_requirement(requirement.choices, self.choice_history)

        return has_items and visited_nodes and made_choices

    def check_requirement(self, requirement_list, player_list):
        return all(item in player_list for item in requirement_list)

    def apply_consequence(self):
        consequence = self.selected_choice.consequence

        if consequence is None:
            return

        if consequence.remove_choice:
            self.current_node.choices.remove(self.selected_choice)

        for item in consequence.items:
            if item.startswith('-'):
                self.inventory.remove(item[1:])
            elif item.startswith('+'):
                self.inventory.append(item[1:])

    def move_to_new_node(self,next_node):
        self.current_node.is_visited = True
        self.node_history.append(self.current_node.id)

        if self.selected_choice:
            self.selected_choice.is_made = True
            self.choice_history.append(self.selected_choice.id)

        self.selected_choice = None
        self.previous_node = self.current_node
        self.current_node = next_node
    
    def game_loop(self):
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
        self.check_node()
        
