from html_model import HTMLModel
from display import render_tree, render_indented
from spellcheck import spell_check
from html_io import read_html_file, write_html_file

class HTMLCommandEditor:
    def __init__(self):
        self.model = HTMLModel()
        self.history = []  # Store history for undo
        self.future = []   # Store future for redo

    def execute_command(self, command, *args):
        if command == "insert":
            self._insert(*args)
        elif command == "append":
            self._append(*args)
        elif command == "delete":
            self._delete(*args)
        elif command == "edit-text":
            self._edit_text(*args)
        elif command == "edit-id":
            self._edit_id(*args)
        elif command == "print-tree":
            print("\n".join(render_tree(self.model.root)))
        elif command == "print-indent":
            indent = int(args[0]) if args else 2
            print(render_indented(self.model.root, indent))
        elif command == "read":
            self.model = read_html_file(args[0])
        elif command == "save":
            write_html_file(args[0], self.model)
        elif command == "spell-check":
            errors = spell_check(self.model.root)
            for error in errors:
                print(f"Element {error[0]}: {error[1]}")
        elif command == "init":
            self.model = HTMLModel()
            print("Initialized HTML model.")
        elif command == "undo":
            self.undo()
        elif command == "redo":
            self.redo()
        else:
            raise ValueError(f"Unknown command: {command}")
        self.history.append((command, args))
        self.future.clear()  # Clear future stack when a new command is executed

    def _insert(self, tag, element_id, parent_id, text_content=""):
        """Insert a new element"""
        self.model.add_element(tag, element_id, parent_id, text_content)

    def _append(self, tag_name, id_value, parent_id, text_content=""):
        """Append a new element to the parent element"""
        # Step 1: Check if the new id already exists
        if self.model.get_element_by_id(id_value):
            print(f"Error: An element with id '{id_value}' already exists.")
            return
        
        # Step 2: Find the parent element by parent_id
        parent_element = self.model.get_element_by_id(parent_id)
        if not parent_element:
            print(f"Error: Parent element with id '{parent_id}' not found.")
            return
        
        # Step 3: Insert the new element as the last child of the parent element
        self.model.add_element(tag_name, id_value, parent_id, text_content)
        print(f"Appended {tag_name} with id '{id_value}' to parent element with id '{parent_id}'.")
    
    
    def _delete(self, element_id):
        """Delete an element"""
        self.model.delete_element(element_id)

    def _edit_text(self, element_id, new_text):
        """Edit an element's text content"""
        self.model.edit_text(element_id, new_text)

    def _edit_id(self, old_id, new_id):
        """Edit an element's id"""
        self.model.edit_id(old_id, new_id)

    def undo(self):
        """Undo the last command."""
        if not self.history:
            print("Nothing to undo.")
            return
        
        # Pop the last command from the history and execute the inverse operation
        last_command, args = self.history.pop()
        if last_command == "insert":
            # Undo insert by deleting the element
            self.model.delete_element(args[1])
        elif last_command == "delete":
            # Undo delete by reinserting the element (for simplicity, we don't store the original content)
            tag, element_id, parent_id, text_content = args
            self.model.add_element(tag, element_id, parent_id, text_content)
        elif last_command == "edit-text":
            # Undo edit-text by restoring previous text (store previous text in args)
            element_id, new_text = args
            self.model.edit_text(element_id, new_text)
        elif last_command == "edit-id":
            # Undo edit-id by restoring previous id (store old_id and new_id in args)
            old_id, new_id = args
            self.model.edit_id(new_id, old_id)
        else:
            print("Unsupported undo operation.")
            return
        
        # Move the command to the future stack
        self.future.append((last_command, args))
        print(f"Undo: {last_command} {args}")

    def redo(self):
        """Redo the last undone command."""
        if not self.future:
            print("Nothing to redo.")
            return
        
        # Pop the last undone command and re-execute it
        last_command, args = self.future.pop()
        if last_command == "insert":
            self.model.add_element(*args)
        elif last_command == "delete":
            self.model.delete_element(args[0])
        elif last_command == "edit-text":
            element_id, new_text = args
            self.model.edit_text(element_id, new_text)
        elif last_command == "edit-id":
            old_id, new_id = args
            self.model.edit_id(old_id, new_id)
        else:
            print("Unsupported redo operation.")
            return
        
        # Move the command to the history stack
        self.history.append((last_command, args))
        print(f"Redo: {last_command} {args}")
