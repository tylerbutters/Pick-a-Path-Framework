from Player import Player
from FileManager import FileManager
import os
import time
import sys

class Game:
    player = Player()
    STARTING_NODE_ID = "N1"
    nodes = FileManager.load_all_nodes(FileManager(),STARTING_NODE_ID)
    current_node = nodes[STARTING_NODE_ID]
    previous_node = None   
    selected_choice = None
    previous_selected_choice = None

    @staticmethod
    def print_delay(text):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.00)
        print("")

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')  # For Windows, use 'cls'; for macOS/Linux, use 'clear'

    def display_description(self):
        description = self.current_node.revisited_description if self.current_node.is_visited else self.current_node.description

        lines = description.split('.')
        for line in lines:
            Game.print_delay(line.strip())

    def display_choices(self):
        choices_to_display = []

        for choice in self.current_node.choices:
            if self.check_choice_requirement(choice.requirement):
                choices_to_display.append(choice)     
       
        for choice in self.current_node.choices:
            print(f" [{choice.name.upper()}]",end='')
    
    def select_choice(self):
        while True:
            selected_choice = input('\n').strip().lower()  # Strip any leading/trailing spaces

            # Iterate over choices in the current node
            for choice in self.current_node.choices:
                if selected_choice.lower() == choice.name.lower():
                    self.selected_choice = choice
                    return  # Exit the loop if a matching choice is found

            # Handle case when no matching choice is found
            print("Invalid choice. Please try again.")

    def check_choice_requirement(self, requirement):
        if requirement is None:
            return

        has_items = self.check_requirement(requirement.items, self.player.inventory)
        visited_nodes = self.check_requirement(requirement.node_visits, self.player.node_history)
        made_choices = self.check_requirement(requirement.choices, self.player.choice_history)

        return has_items and visited_nodes and made_choices

    def check_requirement(self, requirement_list, player_list):
        for requirement_item in requirement_list:
            if requirement_item not in player_list:
                return False

        return True

    def apply_consequence(self):
        if self.selected_choice.consequence is None:
            return

        for item in self.selected_choice.consequence.items_to_add:
            self.player.inventory.append(item)
        for item in self.selected_choice.consequence.items_to_remove:
            self.player.inventory.remove(item)

    def navigate_to_next_node(self,next_node):
        print()
        self.previous_selected_choice = self.selected_choice
        self.previous_node = self.current_node
        self.current_node = next_node
    
    def navigate_to_previous_node(self):
        print()
        self.current_node = self.previous_node
        if self.previous_selected_choice.target_node:
            self.previous_node = self.previous_selected_choice.target_node

    def game_loop(self):       
        self.display_description()
        self.current_node.is_visited = True
        if not self.current_node.choices:
            if self.current_node.target_node and self.current_node.target_node.id is not self.current_node.id: # continuation node
                self.navigate_to_next_node(self.current_node.target_node)
            else:
                self.navigate_to_previous_node() # rebound node
            return
        self.display_choices()
        self.select_choice()
        Game.clear()
        self.apply_consequence()
        self.navigate_to_next_node(self.selected_choice.target_node)
