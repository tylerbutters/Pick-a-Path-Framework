class Choice:
    def __init__(self, id, name, visibility_requirement, navigation_requirement, consequence, true_node, false_node):
        self.id = id
        self.name = name
        self.visibility_requirement = visibility_requirement
        self.navigation_requirement = navigation_requirement
        self.consequence = consequence
        self.true_node = true_node
        self.false_node = false_node       
