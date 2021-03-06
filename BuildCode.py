import os
from PlantContent import PlantContent


class BuildCode:
    """ 
    Creates the output files used to generate the diagram, and if configured will
    generate the diagram in the format specified in the json configuration
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
        self.__maybe_setup_one_file()
        if not self.typelist_hidden:
            self.typelist_builder(True)
            self.typelist_builder(False)
        if not self.delegate_hidden:
            self.delegate_builder(True)
            self.delegate_builder(False)
        self.entity_builder(True)
        self.entity_builder(False)
        if self.one_file:
            self.current_file.write('@enduml\n')
            self.current_file.close()
        self.__maybe_create_diagram()

    def extend_core(self):
        """
        When core association is true and core entities are being processed this function will add the
        additional entities to the list of the core entities to allow then to be processed
        """
        if not (self.config_json['core_only'].lower() == 'true'):
            return self
        if not (self.config_json['core_associations'].lower() == 'true'):
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
        if self.one_file is not True:
            self.current_file = open(entity_file_name, 'w')
            self.current_file.write(f"@startuml {uml_name}\n\n")
            self.current_file.write("!include BaseDelegate.puml\n")
            if not self.config_json['typelist_hidden'].lower() == 'true':
                self.current_file.write("!include BaseTypelist.puml\n\n")
            if not metadata:
                if not self.config_json['plantuml_theme'] == '':
                    plant_theme = '!theme ' + self.config_json['plantuml_theme']
                    self.current_file.write(f'{plant_theme} \n')
                self.current_file.write("!include BaseEntity.puml\n")
                if not self.config_json['typelist_hidden'].lower() == 'true':
                    self.current_file.write("!include ExtensionTypelist.puml\n")
                self.current_file.write("!include ExtensionDelegate.puml\n\n")
            if self.config_json['remove_unlinked'].lower() == 'true':
                self.current_file.write("remove @unlinked\n\n")
        if self.config_json['plantuml_theme'] == '':
            self.current_file.write('skinparam class {\n')
            self.current_file.write(f'\tBackgroundColor<<{stereotype}>> {class_colour}\n')
            self.current_file.write('}\n\n')
        for structure in self.plant_structures:
            if structure.type == 'entity' or structure.type == 'subtype':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and not (structure.metadata == 'true'):
                    process = True
                if process:
                    process = self.__process_item(structure.name)
                if process:
                    self.current_file.write(f'class {structure.name} <<{structure.stereotype}>>' + ' {\n')
                    if self.config_json['entity_contents'].lower() == 'true':
                        for key, value in structure.columns.items():
                            self.current_file.write(f'\t{key} : {value}\n')
                    self.current_file.write('} \n')
                    self.__write_implements(structure)
                    self.__write_arrays(structure)
                    self.__write_typekeys(structure)
                    self.__write_foreign_keys(structure)
                    if structure.type == 'subtype':
                        self.current_file.write(f'{structure.name} --|> {structure.subtype}\n')
                    self.current_file.write("\n")
        if self.one_file is not True:
            self.current_file.write("@enduml\n")
            self.current_file.close()
        return self

    def delegate_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Delegates
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
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
        if self.one_file is not True:
            self.current_file = open(delegate_file_name, 'w')
            self.current_file.write(f"@startuml {uml_name}\n")
        if self.config_json['plantuml_theme'] == '':
            self.current_file.write('skinparam class {\n')
            self.current_file.write(f'\tBackgroundColor<<Delegate>> {class_colour}\n')
            self.current_file.write('}\n\n')
        for structure in self.plant_structures:
            if structure.type == 'delegate':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and not (structure.metadata == 'true'):
                    process = True
                if process:
                    process = self.__process_item(structure.name)
                if process:
                    self.current_file.write(f'abstract {structure.name} <<{structure.stereotype}>>' + ' {\n')
                    if self.config_json['delegate_contents'].lower() == 'true':
                        for key, value in structure.columns.items():
                            self.current_file.write(f'\t{key} : {value}\n')
                    self.current_file.write('} \n')
                    self.__write_implements(structure)
                    self.__write_arrays(structure)
                    self.__write_typekeys(structure)
                    self.__write_foreign_keys(structure)
                    self.current_file.write("\n")
        if self.one_file is not True:
            self.current_file.write("@enduml\n")
            self.current_file.close()
        return self

    def typelist_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Typelists
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        target_file_name = self.target_path
        if metadata:
            target_file_name = target_file_name + "/BaseTypelist.puml"
            uml_name = 'BaseTypelists'
            print("typelists - Metadata")
        else:
            target_file_name = target_file_name + "/ExtensionTypelist.puml"
            uml_name = 'ExtensionTypelist'
            print("typelists - Extensions")
        if self.one_file is not True:
            self.current_file = open(target_file_name, 'w')
            self.current_file.write(f"@startuml {uml_name}\n\n")
        if self.config_json['plantuml_theme'] == '':
            self.current_file.write('skinparam enum {\n')
            self.current_file.write(f'\tBackgroundColor<<typelist>> {self.config_json["typelist_colour"]}\n')
            self.current_file.write('}\n\n')
        for structure in self.plant_structures:
            if structure.type == 'typelist':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and not (structure.metadata == 'true'):
                    process = True
                if process:
                    process = self.__process_item(structure.name)
                if process:
                    self.current_file.write(f'enum {structure.name} <<{structure.stereotype}>>' + ' {\n')
                    self.__write_typelist_contents(structure)
                    self.current_file.write('} \n\n')
        if self.one_file is not True:
            self.current_file.write("@enduml\n")
            self.current_file.close()
        return self

    def __write_implements(self, structure: PlantContent):
        for key, value in structure.implements_entities.items():
            if self.__process_item(value):
                self.current_file.write(f'{structure.name} ..> {value}\n')

    def __write_arrays(self, structure: PlantContent):
        for key, value in structure.arrays.items():
            if self.__process_item(value):
                self.current_file.write(f'{structure.name} *-- "{key}" {value}\n')

    def __write_typekeys(self, structure: PlantContent):
        for key, value in structure.type_keys.items():
            if self.__process_item(key):
                self.current_file.write(f'{structure.name} --> "{value}" {key}\n')

    def __write_foreign_keys(self, structure: PlantContent):
        for key, value in structure.foreign_keys.items():
            if self.__process_item(value):
                self.current_file.write(f'{structure.name} --> "{key}" {value}\n')

    def __write_typelist_contents(self, structure):
        if self.config_json['typelist_contents'].lower() == 'true':
            for key, value in structure.type_codes.items():
                self.current_file.write(f'\t{key}\n')

    def __maybe_setup_one_file(self):
        if not self.one_file:
            return
        write_file = self.target_path + '/' + self.config_json['one_file_name'] + '.puml'
        self.current_file = open(write_file, 'w')
        self.current_file.write('@startuml ' + self.config_json['one_file_name'] + '\n\n')
        if not self.config_json['plantuml_theme'] == '':
            plant_theme = '!theme ' + self.config_json['plantuml_theme']
            self.current_file.write(f'{plant_theme} \n')
        if self.config_json['remove_unlinked'].lower() == 'true':
            self.current_file.write("remove @unlinked\n\n")

    def __maybe_create_diagram(self):
        if not self.generate_diagram:
            return

        command = 'java -DPLANTUML_LIMIT_SIZE=' + self.config_json['plantuml_limit_size']
        command = command + ' -jar ' + self.config_json['local_plantuml_jar']
        command = command + ' ' + self.config_json['diagram_format_flag']
        if self.config_json['diagram_verbose'].lower() == 'true':
            command = command + ' -verbose '
        else:
            command = command + ' '
        if self.one_file:
            write_file = self.target_path + '/' + self.config_json['one_file_name'] + '.puml'
            command = command + write_file
        else:
            command = command + self.target_path + "/ExtensionEntity.puml"
        print(command)
        os.system(command)

    def __process_item(self, in_item_name) -> bool:
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
        self.one_file = False
        self.current_file = None

        if self.config_json['typelist_hidden'].lower() == 'true':
            self.typelist_hidden = True
        else:
            self.typelist_hidden = False

        if self.config_json['delegate_hidden'].lower() == 'true':
            self.delegate_hidden = True
        else:
            self.delegate_hidden = False

        if self.config_json['generate_diagram'].lower() == 'true':
            self.generate_diagram = True
        else:
            self.generate_diagram = False

        if self.config_json['one_file'].lower() == 'true':
            self.one_file = True

        for entity in self.config_json["core_entities"]:
            self.core_entities.append(entity["core_entity"])
