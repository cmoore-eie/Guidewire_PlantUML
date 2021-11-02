import os
from PlantContent import PlantContent

class BuildCode:
    """ 
    Creates the output files used to generate the diagram, and if configured will
    generate the diagem in the fromat specified in the json configuration
    """

    def type_builder(self):
        """
        Main function to process the information and generate the puml output files, if configured
        the diagram will also be created based on the generated output files
        """
        print('')
        print("Processing Entities")
        print("===================")
        self.extend_core()
        if not self.config_json['typelist_hidden'].lower() == 'true':
            self.typelist_builder(True)
            self.typelist_builder(False)
        self.delegate_builder(True)
        self.delegate_builder(False)
        self.entity_builder(True)
        self.entity_builder(False)
        if self.config_json['generate_diagram'].lower() == 'true':
            command = 'java -DPLANTUML_LIMIT_SIZE=' + self.config_json['plantuml_limit_size']
            command = command + ' -jar ' + self.config_json['local_plantuml_jar'] 
            command = command + ' ' + self.config_json['diagram_format_flag']
            if self.config_json['diagram_verbose'].lower() == 'true':
                command = command + ' -verbose '
            else:
                command = command + ' '
            command = command + self.target_path + "/ExtensionEntity.puml"
            print(command)
            os.system(command)

    def extend_core(self):
        """
        When core association is true and core entities are being processed this function will add the
        additional entities to the list of the core entities to alow then to be processed
        """
        if not(self.config_json['core_only'].lower() == 'true'):
            return self
        if not(self.config_json['core_associations'].lower() == 'true'):
            return self
        for core_name in self.core_entities.copy():
            structure: PlantContent
            for check_structure in self.plant_structures:
                if check_structure.name == core_name:
                    structure = check_structure
            for key, value in structure.arrays.items():
                self.core_entities.append(value)
            if not self.config_json['typelist_hidden'].lower() == 'true':
                for key, value in structure.type_keys.items():
                    jsonval = self.config_json['typelist_hidden']
                    self.core_entities.append(key)
            for key, value in structure.foreign_keys.items():
                self.core_entities.append(value)


    def entity_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Entities and Subtypes
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        entity_file_name = self.target_path
        if metadata:
            entity_file_name = entity_file_name + "/BaseEntity.puml"
            uml_name = 'BaseEntity'
            class_colour = self.config_json['meta_entity_colour']
            stereotype = "Base"
            print("entities - Metadata")
        else:
            entity_file_name = entity_file_name + "/ExtensionEntity.puml"
            uml_name = 'ExtensionEntity'
            class_colour = self.config_json['entity_colour']
            stereotype = "Entity"
            print("entities - Extensions")
        file = open(entity_file_name, 'w')
        file.write(f"@startuml {uml_name}\n\n")
        file.write("!include BaseDelegate.puml\n")
        if not self.config_json['typelist_hidden'].lower() == 'true':
            file.write("!include BaseTypelist.puml\n\n")
        if not metadata:
            file.write("!include BaseEntity.puml\n")
            if not self.config_json['typelist_hidden'].lower() == 'true':
                file.write("!include ExtensionTypelist.puml\n")
            file.write("!include ExtensionDelegate.puml\n\n")
        if self.config_json['remove_unlinked'].lower() == 'true':
            file.write("remove @unlinked\n\n")
        file.write('skinparam class {\n')
        file.write(f'\tBackgroundColor<<{stereotype}>> {class_colour}\n')
        file.write('}\n')
        file.write('\n')
        for structure in self.plant_structures:
            if structure.type == 'entity' or structure.type == 'subtype':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and not (structure.metadata == 'true'):
                    process = True
                if process:
                    process = self.process_item(structure.name)
                if process:
                    file.write(f'class {structure.name} <<{structure.stereotype}>>' + ' {\n')
                    if self.config_json['entity_contents'].lower() == 'true':
                            for key, value in structure.columns.items():
                                file.write(f'\t{key} : {value}\n')
                    file.write('} \n')
                    for key, value in structure.implements_entities.items():
                        if self.process_item(value):
                          file.write(f'{structure.name} ..> {value}\n')
                    for key, value in structure.arrays.items():
                        if self.process_item(value):
                          file.write(f'{structure.name} *-- "{key}" {value}\n')
                    for key, value in structure.type_keys.items():
                        if self.process_item(key):
                          file.write(f'{structure.name} --> "{value}" {key}\n')
                    for key, value in structure.foreign_keys.items():
                        if self.process_item(value):
                          file.write(f'{structure.name} --> "{key}" {value}\n')
                    if structure.type == 'subtype':
                        file.write(f'{structure.name} --|> {structure.subtype}\n')
                    file.write("\n")
        file.write("@enduml\n")
        file.close()
        return self

    def delegate_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Delegates
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        uml_name = ''
        steryotype = ''
        class_colour = ''
        if metadata:
            delegate_file_name = self.target_path + "/BaseDelegate.puml"
            uml_name = 'BaseDelegate'
            class_colour = self.config_json['delegate_colour']
            print("delegates - Metadata")
        else:
            delegate_file_name = self.target_path + "/ExtensionDelegate.puml"
            uml_name = 'ExtensionDelegate'
            class_colour = self.config_json['delegate_colour']
            print("delegates - Extensions")
        file = open(delegate_file_name, 'w')
        file.write(f"@startuml {uml_name}\n")
        file.write('skinparam class {\n')
        file.write(f'\tBackgroundColor<<Delegate>> {class_colour}\n')
        file.write('}\n')
        file.write('\n')
        for structure in self.plant_structures:
            if structure.type == 'delegate':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and not (structure.metadata == 'true'):
                    process = True
                if process:
                    process = self.process_item(structure.name)
                if process:
                    file.write(f'abstract {structure.name} <<{structure.stereotype}>>' + ' {\n')
                    if self.config_json['delegate_contents'].lower() == 'true':
                        for key, value in structure.columns.items():
                            file.write(f'\t{key} : {value}\n')
                    file.write('} \n')
                    for key, value in structure.implements_entities.items():
                        if self.process_item(value):
                            file.write(f'{structure.name} ..> {value}\n')
                    for key, value in structure.arrays.items():
                        if self.process_item(value):
                            file.write(f'{structure.name} *-- "{key}" {value}\n')
                    for key, value in structure.type_keys.items():
                        if self.process_item(key):
                            file.write(f'{structure.name} --> "{value}" {key}\n')
                    for key, value in structure.foreign_keys.items():
                        if self.process_item(value):
                            file.write(f'{structure.name} --> "{key}" {value}\n')
                    file.write("\n")
        file.write("@enduml\n")
        file.close()
        return self

    def typelist_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Typelists
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        target_file_name = self.target_path
        uml_name = ''
        if metadata:
            target_file_name = target_file_name + "/BaseTypelist.puml"
            uml_name = 'BaseTypelists'
            print("typelists - Metadata")
        else:
            target_file_name = target_file_name + "/ExtensionTypelist.puml"
            uml_name = 'ExtensionTypelist'
            print("typelists - Extensions")
        file = open(target_file_name, 'w')
        file.write(f"@startuml {uml_name}\n\n")
        file.write('skinparam enum {\n')
        file.write(f'\tBackgroundColor<<typelist>> {self.config_json["typelist_colour"]}\n')
        file.write('}\n')
        file.write('\n')
        for structure in self.plant_structures:
            if structure.type == 'typelist':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and not (structure.metadata == 'true'):
                    process = True
                if process:
                    process = self.process_item(structure.name)
                if process:
                    file.write(f'enum {structure.name} <<{structure.stereotype}>>' + ' {\n')
                    if self.config_json['typelist_contents'].lower() == 'true':
                        for key, value in structure.type_codes.items():
                            file.write(f'\t{key}\n')
                    file.write('} \n\n')
        file.write("@enduml\n")
        file.close()
        return self

    def process_item(self, in_item_name) -> bool:
        """
        Identifies if an entity should be processed or not, this is based on the information in the
        json configuration file.

        Parameters
        ==========
        in_item_name - The name of the entity to be checked.

        Return
        ======
        True - if the item specified by the passed name should be included in the output files.
        False - if the item should not be included in the output files
        """
        process: bool = False
        if self.config_json['include_custom'].lower() == 'true':
            if in_item_name.find(self.config_json['custom_prefix']) >= 0:
                return True
        if self.core_only == 'true':
            if in_item_name in self.core_entities:
                process = True
        else:
            process = True
        return process

    def __init__(self, in_config_json, in_plant_structures: list[PlantContent]):
        self.config_json = in_config_json
        self.plant_structures = in_plant_structures
        self.target_path = self.config_json['target_path']
        self.core_only = self.config_json['core_only']
        self.core_entities: list[str] = list()
        for entity in self.config_json["core_entities"]:
            self.core_entities.append(entity["core_entity"])
