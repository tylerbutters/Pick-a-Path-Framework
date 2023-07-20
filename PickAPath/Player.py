class Player:
    def __init__(self):
        self.inventory = []
        self.node_history = []
        self.choice_history = []

    def display_inventory(self):
        print("[INVENTORY]")
        if not self.inventory:
            print("Empty")
            return
        print(self.inventory)
