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
        if len(row) >= 5:
            node_id = row[0]
            node = Node(
                node_id,
                title=row[1],
                description=row[2],
                source_node_ids=[attribute for attribute in row[3:] if attribute.startswith('N')],
                choice_ids=[attribute for attribute in row[3:] if attribute.startswith('C')],
                source_nodes=None,
                choices=None
            )
            return node
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    def create_choice(self, row):
        if len(row) >= 5:
            choice_id = row[0]
            choice = Choice(
                choice_id,
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
            requirement_id = row[0]
            requirement = Requirement(requirement_id)
            return requirement
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    def create_consequence(self, row):
        if len(row) >= 1:
            consequence_id = row[0]
            consequence = Consequence(consequence_id)
            return consequence
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return


    def load_all_nodes(self, starting_node_id):
        nodes = {}
        starting_node = FileManager.load_node(self, starting_node_id)
        nodes[starting_node_id] = starting_node

        return nodes

    def load_node(self, node_id):
        if node_id == "0" or node_id in FileManager.node_cache:
            return

        node = self.node_rows.get(node_id)
        if node is None:
            return

        # Mark the choice as loaded to avoid potential infinite recursion
        FileManager.node_cache[node_id] = node

        node.source_nodes = [FileManager.load_node(self, source_node_id) for source_node_id in node.source_node_ids]
        node.choices = [FileManager.load_choice(self, choice_id) for choice_id in node.choice_ids]
        
        return node

    def load_choice(self, choice_id):
        if choice_id == "0" or choice_id in FileManager.choice_cache:
            return

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
        if requirement_id == "0" or requirement_id in FileManager.requirement_cache:
            return

        requirement = self.requirement_rows.get(requirement_id)
        if requirement is None:
            return

        # Mark the requirement as loaded to avoid potential infinite recursion
        FileManager.requirement_cache[requirement_id] = requirement

        return requirement

    def load_consequence(self, consequence_id):
        if consequence_id == "0" or consequence_id in FileManager.consequence_cache:
            return

        consequence = self.consequence_rows.get(consequence_id)
        if consequence is None:
            return

        # Mark the consequence as loaded to avoid potential infinite recursion
        FileManager.consequence_cache[consequence_id] = consequence

        return consequence
