from Entities.Node import Node
from Entities.Choice import Choice
from Entities.Consequence import Consequence
from Entities.Requirement import Requirement
from Game import Game
import os
import csv
import logging

class FileManager:
    delimiter = '|'

    FILE_DIRECTORY = "StoryFiles"
    STORY_NAME = "EscapeShed" # Enter story folder name here
    NODE_FILE = "nodes.csv"
    CHOICE_FILE = "choices.csv"
    REQUIREMENT_FILE = "requirements.csv"
    CONSEQUENCES_FILE = "consequences.csv"
    SAVES_FILE = "saves.csv"

    NODE_FILE_PATH = os.path.join(FILE_DIRECTORY, STORY_NAME, NODE_FILE)
    CHOICE_FILE_PATH = os.path.join(FILE_DIRECTORY, STORY_NAME, CHOICE_FILE)
    REQUIREMENT_FILE_PATH = os.path.join(FILE_DIRECTORY, STORY_NAME, REQUIREMENT_FILE)
    CONSEQUENCES_FILE_PATH = os.path.join(FILE_DIRECTORY, STORY_NAME, CONSEQUENCES_FILE)
    SAVES_FILE_PATH = os.path.join(FILE_DIRECTORY, STORY_NAME, SAVES_FILE)

    node_cache = {}
    choice_cache = {}
    requirement_cache = {}
    consequence_cache = {}

    node_data = {}
    choice_data = {}
    requirement_data = {}
    consequence_data = {}
    
    @staticmethod
    def write_saves(saves):
        try:
            with open(FileManager.SAVES_FILE_PATH, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([  # Header row
                    "Name",
                    "Current Node",
                    "Inventory",
                    "Node History",
                    "Choice History",
                ])

                for save in saves:
                    writer.writerow([
                        save.name,
                        save.current_node,
                        FileManager.delimiter.join(save.inventory),
                        FileManager.delimiter.join(save.node_history),
                    ])
        except FileNotFoundError as e:
            logging.error(f"File '{FileManager.SAVES_FILE_PATH}' not found: {e}")
        except IOError as e:
            logging.error(f"Error writing file '{FileManager.SAVES_FILE_PATH}': {e}")

    @staticmethod
    def read_save_files():
        saves = {}
        try:
            with open(FileManager.SAVES_FILE_PATH, 'r', newline='') as file:
                rows = csv.reader(file)
                for row in rows:
                    if rows.line_num == 1:
                        continue  # Skip the header row
                    save = Game(
                        name=row[0],
                        current_node=row[1].upper(),
                        inventory=row[2].split(FileManager.delimiter),
                        node_history=row[3].split(FileManager.delimiter),
                    )
                    saves[save.name] = save
        except FileNotFoundError:
            logging.error(f"File '{FileManager.SAVES_FILE_PATH}' not found.")
        except IOError as e:
            logging.error(f"Error reading file '{FileManager.SAVES_FILE_PATH}': {e}")
        return saves


    @staticmethod
    def read_data(file_path, create_object):
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

    @staticmethod
    def create_node(row):
        if row[0] == "<END>":
            return Node(
                id=row[0],
                name=row[1],
                description=row[2],
                revisited_description=None,
                target_node=None,
                choices=None
                )
        if len(row) >= 5:
            node = Node(
                id = row[0].upper(),
                name = row[1],
                description = row[2],
                revisited_description = row[3],
                target_node = row[4],
                choices = row[5].split(FileManager.delimiter) if len(row) > 5 and row[5] else None,
            )

            if not isinstance(node, Node):
                logging.error("Error creating node:", row)
                return
            return node
        else:
            logging.error(f"Invalid attribute count in row: {row}\nRow count should be: 6 but it's: {len(row)}'")
            return

    @staticmethod
    def create_choice(row):
        if len(row) >= 6:
            choice = Choice(
                id=row[0].upper(),
                name=row[1],
                visibility_requirement=row[2].upper(),
                navigation_requirement=row[3].upper(),
                consequence=row[4].upper(),
                true_node=row[5].upper(),
                false_node=row[6].upper() if len(row) == 7 and row[6] else None
            )
            if choice is None:
                logging.error(f"Error creating choice: {row}")
            return choice
        else:
            logging.error(f"Invalid attribute count in row: {row.id}\nRow count should be: 6 but it's: {len(row)}'")
            return
    
    @staticmethod
    def create_requirement(row):
        if len(row) >= 1:
            requirement = Requirement(
                id=row[0].upper(),
                items=row[1].split(FileManager.delimiter) if len(row) >= 2 and row[1] else None,
                node_visits = [item.upper() for item in row[2].split(FileManager.delimiter)] if len(row) >= 3 and row[2] else None
            )
            if requirement is None:
                logging.error(f"Error creating requirement: {row}")
            return requirement
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return


    @staticmethod
    def create_consequence(row):
        if len(row) >= 1:
            consequence = Consequence(
                id=row[0].upper(),
                remove_choice=row[1].lower() == 'true',  # Convert 'True'/'False' to a boolean
                items = row[2].split(FileManager.delimiter) if len(row) >= 3 and row[2] else None,
            )
            if consequence is None:
                logging.error(f"Error creating consequence: {row}")
            return consequence
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    @staticmethod
    def load_all_nodes():
        nodes = {}
        FileManager.node_data = FileManager.read_data(FileManager.NODE_FILE_PATH, FileManager.create_node)
        FileManager.choice_data = FileManager.read_data(FileManager.CHOICE_FILE_PATH, FileManager.create_choice)
        FileManager.requirement_data = FileManager.read_data(FileManager.REQUIREMENT_FILE_PATH, FileManager.create_requirement)
        FileManager.consequence_data = FileManager.read_data(FileManager.CONSEQUENCES_FILE_PATH, FileManager.create_consequence)
        # Loads starting node which in turn loads all the other objects as it branches out
        FileManager.load_node("<START>")
        nodes.update(FileManager.node_cache)

        # Cleans caches
        FileManager.node_cache.clear()
        FileManager.choice_cache.clear()
        FileManager.requirement_cache.clear()
        FileManager.consequence_cache.clear()

        return nodes

    @staticmethod
    def load_node(node_id):
        node_id = node_id.upper()
        if node_id in FileManager.node_cache:
            return FileManager.node_cache.get(node_id)

        node = FileManager.node_data.get(node_id)
        if node is None:
            logging.error(f"Cannot find node in data: {node_id}")
            return None

        print(f"Loading Node: {node.id}")
        FileManager.node_cache[node_id] = node

        if node.target_node:
            node.target_node = FileManager.load_node(node.target_node)
        elif node.choices:
            node.choices = [FileManager.load_choice(choice_id) for choice_id in node.choices]        
        
        print(f"Loaded Node: {node.id}")

        return node

    @staticmethod
    def load_choice(choice_id):
        choice_id = choice_id.upper()
        if choice_id in FileManager.choice_cache:
            return FileManager.choice_cache.get(choice_id)

        choice = FileManager.choice_data.get(choice_id)
        if choice is None:
            logging.error(f"Cannot find choice in data: {choice_id}")
            return None

        print(f"Loading Choice: {choice.id}")
        FileManager.choice_cache[choice_id] = choice

        choice.visibility_requirement = FileManager.load_requirement(choice.visibility_requirement)
        choice.navigation_requirement = FileManager.load_requirement(choice.navigation_requirement)
        choice.consequence = FileManager.load_consequence(choice.consequence)
        choice.true_node = FileManager.load_node(choice.true_node)
        if choice.false_node: 
            choice.false_node = FileManager.load_node(choice.false_node)

        print(f"Loaded Choice: {choice.id}")

        return choice

    @staticmethod
    def load_requirement(requirement_id):
        if requirement_id == '':
            return None
        if requirement_id in FileManager.requirement_cache:
            return FileManager.requirement_cache.get(requirement_id)

        requirement = FileManager.requirement_data.get(requirement_id)
        if requirement is None:
            logging.error(f"Cannot find requirement in data: {requirement_id}")
            return None

        print(f"Loading Requirement: {requirement.id}")
        FileManager.requirement_cache[requirement_id] = requirement
        print(f"Loaded Requirement: {requirement.id}")

        return requirement

    @staticmethod
    def load_consequence(consequence_id):
        if consequence_id == '':
            return None
        if consequence_id in FileManager.consequence_cache:
            return FileManager.consequence_cache.get(consequence_id)

        consequence = FileManager.consequence_data.get(consequence_id)
        if consequence is None:
            logging.error(f"Cannot find consequence in data: {consequence_id}")
            return None

        print(f"Loading Consequence: {consequence.id}")
        FileManager.consequence_cache[consequence_id] = consequence
        print(f"Loaded Consequence: {consequence.id}")

        return consequence
