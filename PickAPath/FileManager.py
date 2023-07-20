from Game import Game
from Node import Node
from Choice import Choice
from Consequence import Consequence
from Requirement import Requirement
import os
import csv
import logging

class FileManager:
    FILE_DIRECTORY = "RIO"
    NODE_FILE = "nodes.csv"
    CHOICE_FILE = "choices.csv"
    REQUIREMENT_FILE = "requirements.csv"
    CONSEQUENCES_FILE = "consequences.csv"
    SAVES_FILE = "saves.csv"

    NODE_FILE_PATH = os.path.join(FILE_DIRECTORY, NODE_FILE)
    CHOICE_FILE_PATH = os.path.join(FILE_DIRECTORY, CHOICE_FILE)
    REQUIREMENT_FILE_PATH = os.path.join(FILE_DIRECTORY, REQUIREMENT_FILE)
    CONSEQUENCES_FILE_PATH = os.path.join(FILE_DIRECTORY, CONSEQUENCES_FILE)
    SAVES_FILE_PATH = os.path.join(FILE_DIRECTORY, SAVES_FILE)

    node_cache = {}
    choice_cache = {}
    requirement_cache = {}
    consequence_cache = {}
    
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
                        nodes = None,
                        name=row[0],
                        current_node=row[1],
                        previous_node=row[2],
                        previous_selected_choice=row[3],
                        inventory=[attribute for attribute in row[4:] if not attribute.startswith('C') and not attribute.startswith('N')],
                        node_history=[attribute for attribute in row[4:] if attribute.startswith('N')],
                        choice_history=[attribute for attribute in row[4:] if attribute.startswith('C')],
                        )
                    saves[save.name] = save               
        except FileNotFoundError:
            logging.error(f"File '{FileManager.SAVES_FILE_PATH}' not found.")
        except IOError as e:
            logging.error(f"Error reading file '{FileManager.SAVES_FILE_PATH}': {e}")
        return saves

    def write_saves(saves):
        try:
            with open(FileManager.SAVES_FILE_PATH, 'w', newline='') as file:
                writer = csv.writer(file)             
                writer.writerow([ # Header row
                    "Name",
                    "Current Node",
                    "Previous Node",
                    "Previous Selected Choice",
                    "Inventory/Node History/Choice History",
                ])

                # Write each saved game as a row in the CSV file
                for save in saves.values():
                    writer.writerow([
                        save.name,
                        save.current_node.id,
                        save.previous_node.id if save.previous_node else "",
                        save.previous_selected_choice.id if type(save.previous_selected_choice) is Choice else save.previous_selected_choice,
                        *save.inventory,
                        *[node_id for node_id in save.node_history],
                        *[choice_id for choice_id in save.choice_history],
                    ])

        except FileNotFoundError:
            logging.error(f"File '{FileManager.SAVES_FILE_PATH}' not found.")
        except IOError as e:
            logging.error(f"Error writing file '{FileManager.SAVES_FILE_PATH}': {e}")


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
        if len(row) >= 5: # must have id, name, desc, revisited desc and other object
            node_id = row[0]
            name = row[1]
            description = row[2].replace('\r\n','\n')
            revisited_description = row[3]
            target_node_id = row[4]
            choice_ids = [attribute for attribute in row[4:] if attribute.startswith('C')]

            if target_node_id and not choice_ids:
                # Non-choice node
                node = Node(
                    id=node_id,
                    name=name,
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
                    name=name,
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

    @staticmethod
    def create_choice(row):
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
    
    @staticmethod
    def create_requirement(row):
        if len(row) >= 1:
            requirement = Requirement(
                id=row[0],
                items=[attribute.lower() for attribute in row[1:] if not attribute[1:].startswith('C') and not attribute[1:].startswith('N')],
                node_visits=[attribute for attribute in row[1:] if attribute[1:].startswith('N')],
                choices=[attribute for attribute in row[1:] if attribute.startswith('C')],
            )
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
            return consequence
        else:
            logging.error(f"Invalid attribute count in row: {row}")
            return

    @staticmethod
    def load_all_nodes():
        STARTING_NODE_ID = "N1" 
        nodes = {}
        #loads starting node which in turn loads all the other objects as it branches out
        FileManager.load_node(STARTING_NODE_ID)
        nodes.update(FileManager.node_cache)

        #cleans caches
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
            return
        print(f"Loading Node: {node.id}")

        # Mark the choice as loaded to avoid potential infinite recursion
        FileManager.node_cache[node_id] = node

        if node.target_node_id and not node.choice_ids:
            node.target_node = FileManager.load_node(node.target_node_id)
        else:
            node.choices = [FileManager.load_choice(choice_id) for choice_id in node.choice_ids]        
        
        print(f"Loaded Node: {node.id}")
        return node

    @staticmethod
    def load_choice(choice_id):
        if choice_id in FileManager.choice_cache:
            return FileManager.choice_cache.get(choice_id)

        choice_rows = FileManager.read_data(FileManager.CHOICE_FILE_PATH, FileManager.create_choice)
        choice = choice_rows.get(choice_id)
        if choice is None:
            return
        print(f"Loading Choice: {choice.id}")

        # Mark the choice as loaded to avoid potential infinite recursion
        FileManager.choice_cache[choice_id] = choice

        choice.requirement = FileManager.load_requirement(choice.requirement_id)
        choice.consequence = FileManager.load_consequence(choice.consequence_id)
        choice.target_node = FileManager.load_node(choice.target_node_id)

        print(f"Loaded Choice: {choice.id}")
        return choice

    @staticmethod
    def load_requirement( requirement_id):
        if requirement_id == '':
            return
        if requirement_id in FileManager.requirement_cache:
            return FileManager.requirement_cache.get(requirement_id)

        requirement_rows = FileManager.read_data(FileManager.REQUIREMENT_FILE_PATH, FileManager.create_requirement)
        requirement = requirement_rows.get(requirement_id)
        if requirement is None:
            return
        print(f"Loading Requirement: {requirement.id}")
        # Mark the requirement as loaded to avoid potential infinite recursion
        FileManager.requirement_cache[requirement_id] = requirement

        print(f"Loaded Requirement: {requirement.id}")
        return requirement

    @staticmethod
    def load_consequence(consequence_id):
        if consequence_id == '':
            return
        if consequence_id in FileManager.consequence_cache:
            return FileManager.consequence_cache.get(consequence_id)

        consequence_rows = FileManager.read_data(FileManager.CONSEQUENCES_FILE_PATH, FileManager.create_consequence)
        consequence = consequence_rows.get(consequence_id)
        if consequence is None:
            return
        print(f"Loading Consequence: {consequence.id}")

        # Mark the consequence as loaded to avoid potential infinite recursion
        FileManager.consequence_cache[consequence_id] = consequence

        print(f"Loaded Consequence: {consequence.id}")
        return consequence
