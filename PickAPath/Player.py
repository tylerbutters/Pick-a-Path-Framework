class Player:
    def __init__(self):
        self.inventory = []
        self.node_history = []
        self.choice_history = []

    def display_inventory(self):
        for item in self.inventory:
            print(item)
