class Choice:
    def __init__(self, id, name, requirement_id, consequence_id, target_node_id, requirement, consequence, target_node):
        self.id = id
        self.name = name
        self.requirement_id = requirement_id
        self.target_node_id = target_node_id
        self.consequence_id = consequence_id
        self.requirement = requirement
        self.target_node = target_node
        self.consequence = consequence
        self.is_made = False
