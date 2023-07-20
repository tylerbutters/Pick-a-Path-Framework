import time
import sys
import os


class Game:
    nodes = {}
    commands = ["help","inventory","exit","save"]

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
        print("")

    def run_command(self,command):
        if command == "/inventory":
            self.display_inventory()
        elif command == "/save":
            print("GAME SAVED!")
            self.save_pending = True
        elif command == "/help":
            print(Game.commands)

    def display_description(self):
        description = self.current_node.revisited_description if self.current_node.is_visited else self.current_node.description
        lines = description.split("\\")
        for line in lines:
            Game.print_delay(line.strip())

    def display_choices(self):
        choices_to_display = []
        for choice in self.current_node.choices: 
            if self.check_choice_requirement(choice.requirement):
                choices_to_display.append(choice)

        for choice in choices_to_display:
            print(f" [{choice.name.upper()}]", end='')
    
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

    def check_choice_requirement(self, requirement):
        if requirement is None:
            return True

        has_items = self.check_requirement(requirement.items, self.inventory)
        visited_nodes = self.check_requirement(requirement.node_visits, self.node_history)
        made_choices = self.check_requirement(requirement.choices, self.choice_history)

        return has_items and visited_nodes and made_choices

    def check_requirement(self, requirement_list, player_list):
        if requirement_list:
            for requirement_item in requirement_list:
                if requirement_item.startswith('+') and requirement_item[1:] not in player_list:
                    return False
                if requirement_item.startswith('-') and requirement_item[1:] in player_list:
                    return False
        return True

    def apply_consequence(self):
        consequence = self.selected_choice.consequence

        if consequence is None:
            return

        if consequence.remove_choice:
            self.current_node.choices.remove(self.selected_choice)

        if consequence.items:
            for item in consequence.items:
                if item.startswith('-'):
                    self.inventory.remove(item[1:])
                if item.startswith('+'):
                    self.inventory.append(item[1:])


    def navigate_to_next_node(self,next_node):
        print()
        self.current_node.is_visited = True
        self.node_history.append(self.current_node.id)
        if self.selected_choice:
            self.selected_choice.is_made = True
            self.choice_history.append(self.selected_choice.id)

        self.previous_selected_choice = self.selected_choice
        self.selected_choice = None
        self.previous_node = self.current_node
        self.current_node = next_node
    
    def game_loop(self):
        self.display_description()
        if not self.current_node.choices: # continuation or rebound node
            if self.current_node.target_node:
                next_node = self.current_node.target_node
        else: # branch node
            self.display_choices()
            self.select_choice()
            if not self.continue_loop:
                return
            Game.clear()
            self.apply_consequence()
            next_node = self.selected_choice.target_node

        self.navigate_to_next_node(next_node)
