import os

import Utilities
from PlantContent import PlantContent


class BuildPUMLCode:
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
        self.add_custom_additions()
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

    def add_custom_additions(self):
        """
        When looking for custom entities the type lists and delegates may be missed as they don't fit with the
        criteria. In these instances when searching for custom entities and type lists or delegates are to
        be shown, the typelist or delegate names are extracted and added to the custom custom_additions.
        """
        if self.typelist_hidden and self.delegate_hidden:
            return self
        if not self.include_custom:
            return self
        for structure in {uml_structure for uml_structure in self.plant_structures
                          if uml_structure.type == 'entity' or uml_structure.type == 'subtype'}:
            if self.__process_custom(structure.name) is True:
                if self.typelist_hidden is False:
                    for key, value in structure.type_keys.items():
                        if key not in self.custom_additions:
                            self.custom_additions.append(key)
                if not self.delegate_hidden:
                    for key, value in structure.implements_entities.items():
                        if key not in self.custom_additions:
                            self.custom_additions.append(key)
        return self

    def extend_core(self):
        """
        When core association is true and core entities are being processed this function will add the
        additional entities to the list of the core entities to allow then to be processed
        """
        if self.config_json['core_only'].lower() != 'true':
            return self
        if self.config_json['core_associations'].lower() != 'true':
            return self
        for core_name in self.core_entities.copy():
            structure: PlantContent = PlantContent()
            for check_structure in self.plant_structures:
                if check_structure.name == core_name:
                    structure = check_structure
            if structure is not None:
                self.core_entities.extend([value for value in structure.arrays.values()])
                if self.typelist_hidden is False:
                    self.core_entities.extend([value for value in structure.type_keys.keys()])
                self.core_entities.extend([value for value in structure.foreign_keys.keys()])

    def entity_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Entities and Subtypes
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        if metadata:
            class_colour = self.config_json['meta_entity_colour']
            stereotype = "Base"
            print("entities - Metadata")
        else:
            class_colour = self.config_json['entity_colour']
            stereotype = "Entity"
            print("entities - Extensions")
        if self.config_json['plantuml_theme'] == '':
            self.current_file.write('skinparam class {\n')
            self.current_file.write(f'\tBackgroundColor<<{stereotype}>> {class_colour}\n')
            self.current_file.write('}\n\n')
        for structure in self.plant_structures:
            if structure.type == 'entity' or structure.type == 'subtype':
                process = False
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and structure.metadata != 'true':
                    process = True
                if process:
                    process = self.__process_item(structure.name)
                if process:
                    namespace = {'config_json': self.config_json, 'structure': structure}
                    if structure.name in self.shell_entities:
                        template_str = Utilities.build_template('class_shell', namespace)
                    else:
                        template_str = Utilities.build_template('class', namespace)
                    self.current_file.write(template_str)
                    self.__write_implements(structure)
                    self.__write_arrays(structure)
                    self.__write_typekeys(structure)
                    self.__write_foreign_keys(structure)
                    self.subtype_builder(structure)
                    self.current_file.write("\n")
        return self

    def subtype_builder(self, structure):
        if structure.type == 'subtype':
            if self.__process_item(structure.subtype) is False:
                subtype_structure = Utilities.find_plant_structure(self.plant_structures, structure.subtype, False)
                namespace = {'config_json': self.config_json, 'structure': subtype_structure}
                if subtype_structure.name in self.shell_entities:
                    template_str = Utilities.build_template('class_shell', namespace)
                else:
                    template_str = Utilities.build_template('class', namespace)
                self.current_file.write(template_str)
            namespace = {'config_json': self.config_json, 'structure': structure}
            template_str = Utilities.build_template('subtype', namespace)
            self.current_file.write(template_str)

    def delegate_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Delegates
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        if metadata:
            print("delegates - Metadata")
        else:
            print("delegates - Extensions")
        for structure in {delegate_structure for delegate_structure in self.plant_structures
                          if delegate_structure.type == 'delegate'}:
            process = False
            if metadata and structure.metadata == 'true':
                process = True
            if not metadata and structure.metadata != 'true':
                process = True
            if process and self.__process_item(structure.name):
                namespace = {'config_json': self.config_json, 'structure': structure}
                template_str = Utilities.build_template('delegate', namespace)
                self.current_file.write(template_str)
                self.__write_implements(structure)
                self.__write_arrays(structure)
                self.__write_typekeys(structure)
                self.__write_foreign_keys(structure)
                self.current_file.write("\n")
        return self

    def typelist_builder(self, metadata: bool):
        """ 
        Builds the output files for metadata and Extensions Typelists
            
        Parameters
        ==========
        metadata - set to True if this is sourced from metadata else False
        """
        if metadata:
            print("typelists - Metadata")
        else:
            print("typelists - Extensions")
        if self.config_json['plantuml_theme'] == '':
            self.current_file.write('skinparam enum {\n')
            self.current_file.write(f'\tBackgroundColor<<typelist>> {self.config_json["typelist_colour"]}\n')
            self.current_file.write('}\n\n')
        for structure in self.plant_structures:
            if structure.type == 'typelist':
                process = False
                if self.is_also_entity(structure) is False:
                    continue
                if metadata and structure.metadata == 'true':
                    process = True
                if not metadata and structure.metadata != 'true':
                    process = True
                if process and self.__process_item(structure.name):
                    namespace = {'config_json': self.config_json, 'structure': structure}
                    template_str = Utilities.build_template('typelist', namespace)
                    self.current_file.write(template_str)
        return self

    def is_also_entity(self, structure: PlantContent) -> bool:
        """If the typelist name is the same as that of another type then the typelist will be referring to subtypes"""
        process = True
        for test_structure in self.plant_structures:
            if test_structure.type != 'typelist':
                if test_structure.name == structure.name:
                    return False
        return process

    def __write_implements(self, structure: PlantContent):
        for key, value in structure.implements_entities.items():
            if self.__process_item(value):
                namespace = {'Name': structure.name, 'ImplementsName': value}
                template_str = Utilities.build_template('implements', namespace)
                self.current_file.write(template_str)

    def __write_arrays(self, structure: PlantContent):
        for key, value in structure.arrays.items():
            if self.__process_item(value):
                namespace = {'Name': structure.name, 'ArrayName': key, 'ArrayType': value}
                template_str = Utilities.build_template('arrays', namespace)
                self.current_file.write(template_str)

    def __write_typekeys(self, structure: PlantContent):
        if self.typelist_hidden is True:
            return
        for key, value in structure.type_keys.items():
            if self.__process_item(key):
                namespace = {'Name': structure.name, 'TypekeyName': value, 'TypekeyType': key}
                template_str = Utilities.build_template('typekeys', namespace)
                self.current_file.write(template_str)

    def __write_foreign_keys(self, structure: PlantContent):
        for key, value in structure.foreign_keys.items():
            if self.__process_item(value):
                namespace = {'Name': structure.name, 'ForeignKeyName': key, 'ForeignKeyType': value}
                template_str = Utilities.build_template('foreignkeys', namespace)
                self.current_file.write(template_str)

    def __maybe_setup_one_file(self):
        if not self.one_file:
            return
        write_file = self.target_path + '/' + self.config_json['one_file_name'] + '.puml'
        self.current_file = open(write_file, 'w')
        self.current_file.write('@startuml ' + self.config_json['one_file_name'] + '\n\n')
        if self.config_json['plantuml_theme'] != '':
            plant_theme = '!theme ' + self.config_json['plantuml_theme']
            self.current_file.write(f'{plant_theme} \n')
        # if self.config_json['remove_unlinked'].lower() == 'true':
        #     self.current_file.write("remove @unlinked\n\n")

    def __maybe_create_diagram(self):
        if not self.generate_diagram:
            return

        command = 'java -DPLANTUML_LIMIT_SIZE=' + self.config_json['plantuml_limit_size']
        command = command + ' -jar ' + self.config_json['local_plantuml_jar']
        command = command + ' ' + self.config_json['diagram_format_flag']
        if self.config_json['diagram_verbose'].lower() == 'true':
            command += ' -verbose '
        else:
            command += ' '
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
        json configuration file. If the item is in the excluded list it will not be processed

        Parameters
        ==========
        in_item_name - The name of the entity to be checked.

        Return
        ======
        True - if the item specified by the passed name should be included in the output files.
        False - if the item should not be included in the output files
        """
        process: bool = False
        if in_item_name in self.exclude_entities:
            return process
        if self.__process_custom(in_item_name) is True:
            return True

        if self.core_only == 'true':
            if in_item_name in self.core_entities:
                process = True
            if in_item_name in self.custom_additions:
                process = True
        else:
            process = True

        return process

    def __process_custom(self, in_item_name) -> bool:
        """
        Identifies if an entity matches the custom criteria.

        Parameters
        ==========
        in_item_name - The name of the entity to be checked.

        Return
        ======
        True - if the item specified by the passed name matches the custom criteria
        False - if the item is not a match for the custom criteria
        """

        if self.config_json['include_custom'].lower() == 'true':
            if 'custom_prefix' in self.config_json:
                if in_item_name.endswith(self.config_json['custom_prefix']) is True:
                    return True
            if 'custom_suffix' in self.config_json:
                if in_item_name.startswith(self.config_json['custom_suffix']) is True:
                    return True
        return False

    def setup_entities(self):
        if 'core_entities' in self.config_json:
            for entity in self.config_json["core_entities"]:
                self.core_entities.append(entity["core_entity"])

        if 'exclude_entities' in self.config_json:
            for entity in self.config_json["exclude_entities"]:
                self.exclude_entities.append(entity["exclude_entity"])

        if 'shell_entities' in self.config_json:
            for entity in self.config_json["shell_entities"]:
                self.shell_entities.append(entity["shell_entity"])

    def __init__(self, in_config_json, in_plant_structures: list[PlantContent]):
        self.config_json = in_config_json
        self.plant_structures = in_plant_structures
        self.target_path = self.config_json['target_path']
        self.core_only = self.config_json['core_only']
        self.core_entities: list[str] = list()
        self.exclude_entities: list[str] = list()
        self.custom_additions: list[str] = list()
        self.shell_entities: list[str] = list()
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

        if self.config_json['include_custom'].lower() != 'true':
            self.include_custom = False
        else:
            self.include_custom = True

        if self.config_json['generate_diagram'].lower() == 'true':
            self.generate_diagram = True
        else:
            self.generate_diagram = False

        if self.config_json['one_file'].lower() == 'true':
            self.one_file = True

        self.setup_entities()
