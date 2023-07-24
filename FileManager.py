from Entities.Node import Node
from Entities.Choice import Choice
from Entities.Consequence import Consequence
from Entities.Requirement import Requirement
from Game import Game
import os
import csv
import logging

class FileManager:
    FILE_DIRECTORY = "StoryFiles"
    STORY_NAME = "ShelfTest" # Enter story folder name here
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
    
    @staticmethod
    def write_saves(saves):
        try:
            with open(FileManager.SAVES_FILE_PATH, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([  # Header row
                    "Name",
                    "Current Node",
                    "Inventory/Node History/Choice History",
                ])

                for save in saves:
                    writer.writerow([
                        save.name,
                        save.current_node,
                        *save.inventory,
                        *[node_id for node_id in save.node_history],
                        *[choice_id for choice_id in save.choice_history],
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
                        current_node=row[1],
                        inventory=[attribute for attribute in row[2:] if not attribute.startswith('C') and not attribute.startswith('N') and not attribute.startswith('<')],
                        node_history=[attribute for attribute in row[2:] if attribute.startswith('N') or attribute.startswith('<')],
                        choice_history=[attribute for attribute in row[2:] if attribute.startswith('C')],
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
        if len(row) >= 5: # must have id, name, desc, revisited desc and other object
            node_id = row[0]
            name = row[1]
            description = row[2]
            revisited_description = row[3]
            target_node_id = row[4] if row[4].startswith('N') else None
            choice_ids = [attribute for attribute in row[4:] if attribute.startswith('C')]

            if target_node_id and not choice_ids:
                # Non-choice node
                node = Node(
                    id=node_id,
                    name=name,
                    description=description,
                    revisited_description=revisited_description,
                    target_node=target_node_id,
                    choices=None
                )
            elif choice_ids:
                # Choice node
                node = Node(
                    id=node_id,
                    name=name,
                    description=description,
                    revisited_description=revisited_description,
                    target_node=None,
                    choices=choice_ids
                )
            else:
                logging.error(f"Node '{node_id}' has neither choices nor target_node defined.\n{row}")
                return

            if node is None:
                logging.error("Error creating node:", row)
            return node
        else:
            logging.error(f"Invalid column count in row: {row}")
            return

    @staticmethod
    def create_choice(row):
        if len(row) >= 5:
            choice = Choice(
                id=row[0],
                name=row[1],
                requirement=row[2],
                consequence=row[3],
                true_node=row[4],
                false_node=row[5] if len(row) > 5 else None
            )
            if choice is None:
                logging.error(f"Error creating choice: {row}")
            return choice
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return
    
    @staticmethod
    def create_requirement(row):
        if len(row) >= 1:
            requirement = Requirement(
                id=row[0],
                items=[attribute.lower() for attribute in row[1:] if not attribute[1:].startswith('C') and not attribute[1:].startswith('N')],
                node_visits=[attribute for attribute in row[1:] if attribute[1:].startswith('N')],
                choices=[attribute for attribute in row[1:] if attribute.startswith('C')],
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
                id=row[0],
                remove_choice=row[1].lower() == 'true',  # Convert 'True'/'False' to a boolean
                items = [item.lower() for item in row[2:]]
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
        if node_id in FileManager.node_cache:
            return FileManager.node_cache.get(node_id)

        node_rows = FileManager.read_data(FileManager.NODE_FILE_PATH, FileManager.create_node)
        node = node_rows.get(node_id)
        if node is None:
            logging.error(f"Invalid node ID: {node_id}")
            return None

        print(f"Loading Node: {node.id}")
        FileManager.node_cache[node_id] = node

        if node.target_node and not node.choices:
            node.target_node = FileManager.load_node(node.target_node)
        elif node.choices and not node.target_node:
            node.choices = [FileManager.load_choice(choice_id) for choice_id in node.choices]        
        
        print(f"Loaded Node: {node.id}")

        return node

    @staticmethod
    def load_choice(choice_id):
        if choice_id in FileManager.choice_cache:
            return FileManager.choice_cache.get(choice_id)

        choice_rows = FileManager.read_data(FileManager.CHOICE_FILE_PATH, FileManager.create_choice)
        choice = choice_rows.get(choice_id)
        if choice is None:
            logging.error(f"Invalid choice ID: {choice_id}")
            return None

        print(f"Loading Choice: {choice.id}")
        FileManager.choice_cache[choice_id] = choice

        choice.requirement = FileManager.load_requirement(choice.requirement)
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

        requirement_rows = FileManager.read_data(FileManager.REQUIREMENT_FILE_PATH, FileManager.create_requirement)
        requirement = requirement_rows.get(requirement_id)
        if requirement is None:
            logging.error(f"Invalid requirement ID: {requirement_id}")
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

        consequence_rows = FileManager.read_data(FileManager.CONSEQUENCES_FILE_PATH, FileManager.create_consequence)
        consequence = consequence_rows.get(consequence_id)
        if consequence is None:
            logging.error(f"Invalid consequence ID: {consequence_id}")
            return None

        print(f"Loading Consequence: {consequence.id}")
        FileManager.consequence_cache[consequence_id] = consequence
        print(f"Loaded Consequence: {consequence.id}")

        return consequence
