class Node:
    def __init__(self, id, name, description, revisited_description, target_node, choices):
        self.id = id
        self.name = name
        self.description = description
        self.revisited_description = revisited_description
        self.target_node = target_node
        self.choices = choices
        self.is_visited = False