from Node import Node
from Choice import Choice
from Consequence import Consequence
from Requirement import Requirement
import os
import csv
import logging

class FileManager:
    FILE_DIRECTORY = "DataFiles"
    NODE_FILE = "nodes.csv"
    CHOICE_FILE = "choices.csv"
    REQUIREMENT_FILE = "requirements.csv"
    CONSEQUENCES_FILE = "consequences.csv"

    NODE_FILE_PATH = os.path.join(FILE_DIRECTORY, NODE_FILE)
    CHOICE_FILE_PATH = os.path.join(FILE_DIRECTORY, CHOICE_FILE)
    REQUIREMENT_FILE_PATH = os.path.join(FILE_DIRECTORY, REQUIREMENT_FILE)
    CONSEQUENCES_FILE_PATH = os.path.join(FILE_DIRECTORY, CONSEQUENCES_FILE)

    node_cache = {}
    choice_cache = {}
    requirement_cache = {}
    consequence_cache = {}

    def __init__(self):
        self.node_rows = self.read_data(FileManager.NODE_FILE_PATH, self.create_node)
        self.choice_rows = self.read_data(FileManager.CHOICE_FILE_PATH, self.create_choice)
        self.requirement_rows = self.read_data(FileManager.REQUIREMENT_FILE_PATH, self.create_requirement)
        self.consequence_rows = self.read_data(FileManager.CONSEQUENCES_FILE_PATH, self.create_consequence)

    def read_data(self, file_path, create_object):
        data = {}
        try:
            with open(file_path, 'r', newline='') as file:
                rows = csv.reader(file)
                for row in rows:
                    if rows.line_num == 1:
                        continue  # Skip the header row
                    obj = create_object(row)
                    if obj:
                        data[obj.id] = obj
        except FileNotFoundError:
            logging.error(f"File '{file_path}' not found.")
        except IOError as e:
            logging.error(f"Error reading file '{file_path}': {e}")
        return data

    def create_node(self, row):
        if len(row) >= 5: # must have id, title, desc, revisited desc and other object
            node_id = row[0]
            title = row[1]
            description = row[2]
            revisited_description = row[3]

            target_node_id = row[4]
            choice_ids = [attribute for attribute in row[4:] if attribute.startswith('C')]

            if target_node_id and not choice_ids:
                # Non-choice node
                node = Node(
                    id=node_id,
                    title=title,
                    description=description,
                    revisited_description=revisited_description,
                    target_node_id=target_node_id,
                    target_node=None,
                    choice_ids=None,
                    choices=None
                )
                node.target_node_id = target_node_id
            elif choice_ids:
                # Choice node
                node = Node(
                    id=node_id,
                    title=title,
                    description=description,
                    revisited_description=revisited_description,
                    target_node_id=None,
                    target_node=None,
                    choice_ids=choice_ids,
                    choices=None
                )
            else:
                logging.error(f"Node '{node_id}' has neither choices nor target_node defined.")
                return

            return node
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    def create_choice(self, row):
        if len(row) >= 5:
            choice = Choice(
                id=row[0],
                name=row[1],
                requirement_id=row[2],
                consequence_id=row[3],
                target_node_id=row[4],
                requirement=None,
                target_node=None,
                consequence=None
            )
            return choice
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    def create_requirement(self, row):
        if len(row) >= 1:
            requirement = Requirement(
                id=row[0]
            )
            return requirement
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    def create_consequence(self, row):
        if len(row) >= 1:
            consequence = Consequence(
                id=row[0]
            )
            return consequence
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return


    def load_all_nodes(self, starting_node_id):
        nodes = {}

        #loads starting node which in turn loads all the other objects as it branches out
        starting_node = FileManager.load_node(self, starting_node_id)
        nodes[starting_node_id] = starting_node

        #cleans caches
        FileManager.node_cache.clear()
        FileManager.choice_cache.clear()
        FileManager.requirement_cache.clear()
        FileManager.consequence_cache.clear()

        return nodes

    def load_node(self, node_id):
        if node_id in FileManager.node_cache:
            return FileManager.node_cache.get(node_id)

        node = self.node_rows.get(node_id)
        if node is None:
            return

        # Mark the choice as loaded to avoid potential infinite recursion
        FileManager.node_cache[node_id] = node

        if node.target_node_id and not node.choice_ids:
            node.target_node = FileManager.load_node(self, node.target_node_id)
        else:
            node.choices = [FileManager.load_choice(self, choice_id) for choice_id in node.choice_ids]        
        
        return node

    def load_choice(self, choice_id):
        if choice_id in FileManager.choice_cache:
            return FileManager.choice_cache.get(choice_id)
        choice = self.choice_rows.get(choice_id)
        if choice is None:
            return

        # Mark the choice as loaded to avoid potential infinite recursion
        FileManager.choice_cache[choice_id] = choice

        choice.requirement = FileManager.load_requirement(self, choice.requirement_id)
        choice.consequence = FileManager.load_consequence(self, choice.consequence_id)
        choice.target_node = FileManager.load_node(self, choice.target_node_id)

        return choice

    def load_requirement(self, requirement_id):
        if requirement_id == '':
            return
        if requirement_id in FileManager.requirement_cache:
            return FileManager.requirement_cache.get(requirement_id)

        requirement = self.requirement_rows.get(requirement_id)
        if requirement is None:
            return

        # Mark the requirement as loaded to avoid potential infinite recursion
        FileManager.requirement_cache[requirement_id] = requirement

        return requirement

    def load_consequence(self, consequence_id):
        if consequence_id == '':
            return
        if consequence_id in FileManager.consequence_cache:
            return FileManager.consequence_cache.get(consequence_id)

        consequence = self.consequence_rows.get(consequence_id)
        if consequence is None:
            return

        # Mark the consequence as loaded to avoid potential infinite recursion
        FileManager.consequence_cache[consequence_id] = consequence

        return consequence
