import os
import subprocess
from lxml import etree
from InitialStructure import PlantContent

core_entities = []


class BuildCode:

    def type_builder(self):
        print("")
        print("Processing Entities")
        print("===================")
        self.typelist_builder(True)
        self.typelist_builder(False)
        self.delegate_builder(True)
        self.delegate_builder(False)
        self.entity_builder(True)
        self.entity_builder(False)
        if self.config_json['generate_diagram'] == 'true':
            command = 'java -DPLANTUML_LIMIT_SIZE=' + self.config_json['plantuml_limit_size']
            command = command + ' -jar ' + self.config_json['local_plantuml_jar'] 
            command = command + ' ' + self.config_json['diagram_format_flag']+ ' -verbose '
            command = command + self.target_path + "/ExtensionEntity.puml"
            os.system(command)

    def entity_builder(self, metadata: bool):
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
        file.write("!include BaseTypelist.puml\n\n")
        if not metadata:
            file.write("!include BaseEntity.puml\n")
            file.write("!include ExtensionTypelist.puml\n")
            file.write("!include ExtensionDelegate.puml\n\n")
        if self.config_json['remove_unlinked'] == 'true':
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
        file.write(f'\tBackgroundColor<<Typelist>> {self.config_json["typelist_colour"]}\n')
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
                    if self.config_json['typelist_contents'] == 'true':
                        for key, value in structure.type_codes.items():
                            file.write(f'\t{key}\n')
                    file.write('} \n\n')
        file.write("@enduml\n")
        file.close()
        return self

    def process_item(self, in_item_name):
        process = False
        if self.config_json['include_custom'] == 'true':
            if in_item_name.find(self.config_json['custom_prefix']) >= 0:
                return True
        if self.core_only == 'true':
            if in_item_name in core_entities:
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
            core_entities.append(entity["core_entity"])
