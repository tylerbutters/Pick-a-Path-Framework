class Node:
    def __init__(self, id, title, description, source_node_ids, choice_ids, source_nodes, choices):
        self.id = id
        self.title = title
        self.description = description
        self.source_node_ids = source_node_ids
        self.choice_ids = choice_ids
        self.source_nodes = source_nodes
        self.choices = choices
        self.is_visited = False