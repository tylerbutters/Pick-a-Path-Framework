class Requirement:
    def __init__(self, id):
        self.id = id
        self.items = []
        self.node_visits = []
        self.choices = []
