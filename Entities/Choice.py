class Choice:
    def __init__(self, id, name, requirement, consequence, true_node, false_node):
        self.id = id
        self.name = name
        self.requirement = requirement
        self.consequence = consequence
        self.true_node = true_node
        self.false_node = false_node       
