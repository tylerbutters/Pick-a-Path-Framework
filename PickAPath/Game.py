from Player import Player
from FileManager import FileManager


class Game:
    STARTING_NODE_ID = "N1"
    nodes = FileManager.load_all_nodes(FileManager(),STARTING_NODE_ID)
    current_node = nodes[STARTING_NODE_ID]

    def __init__(self):
        self.player = Player()
        self.selected_choice = None

    def display_description(self):
        lines = self.current_node.description.split('.')
        for line in lines:
            print(line.strip())


    def display_choices(self):
        choices_to_display = []
        for choice in self.current_node.choices:
            if self.check_choice_requirement(choice.requirement):
                choices_to_display.append(choice)     
       
        for choice in self.current_node.choices:
            print(f" [{choice.name}]",end='')

    def select_choice(self):
        while True:
            selected_choice = input('\n').strip()  # Strip any leading/trailing spaces

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

    def navigate_to_next_node(self):
        self.current_node = self.selected_choice.target_node

    def apply_consequence(self):
        if self.selected_choice.consequence is None:
            return

        for item in self.selected_choice.consequence.items_to_add:
            self.player.inventory.append(item)
        for item in self.selected_choice.consequence.items_to_remove:
            self.player.inventory.remove(item)

    def game_loop(self):
        self.current_node.is_visited = True
        self.display_description()
        self.display_choices()
        self.select_choice()
        self.apply_consequence()
        self.navigate_to_next_node()
