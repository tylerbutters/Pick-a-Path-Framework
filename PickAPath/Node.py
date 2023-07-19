class Node:
    def __init__(self, id, title, description,revisited_description, target_node_id, choice_ids, target_node, choices):
        self.id = id
        self.title = title
        self.description = description
        self.revisited_description = revisited_description
        self.target_node_id = target_node_id
        self.choice_ids = choice_ids
        self.target_node = target_node
        self.choices = choices
        self.is_visited = False