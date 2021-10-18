import os

from lxml import etree


class PlantContent:
    
    def add_column(self, in_column_name: str, in_column_type: str):
        if in_column_name not in self.columns:
            self.columns[in_column_name] = in_column_type

    def add_foreign_key(self, in_foreign_key_name: str, in_foreign_key_entity: str):
        if in_foreign_key_name not in self.foreign_keys:
            self.foreign_keys[in_foreign_key_name] = in_foreign_key_entity

    def add_array(self, in_array_name: str, in_array_entity: str):
        if in_array_name not in self.arrays:
            self.arrays[in_array_name] = in_array_entity

    def add_implements_entity(self, in_entity_name):
        if in_entity_name not in self.implements_entities:
            self.implements_entities[in_entity_name] = in_entity_name

    def add_type_key(self, in_typelist, in_name):
        if in_typelist not in self.type_keys:
            self.type_keys[in_typelist] = in_name

    def add_type_code(self, in_type_code: str, in_type_name: str):
        if in_type_code not in self.type_codes:
            self.type_codes[in_type_code] = in_type_name

    def __init__(self):
        self.name: str = ''
        self.type: str = ''
        self.stereotype: str = ''
        self.subtype: str = ''
        self.metadata: str = ''
        self.columns: dict[str, str] = dict()
        self.arrays: dict[str, str] = dict()
        self.implements_entities: dict[str, str] = dict()
        self.foreign_keys: dict[str, str] = dict()
        self.type_keys: dict[str, str] = dict()
        self.type_codes: dict[str, str] = dict()


class BuildStructure:

    def build(self):
        self.process_entity(True)
        self.process_entity(False)
        self.process_typelist(True)
        self.process_typelist(False)

    def process_entity(self, metadata: bool):
        path: str = ''
        if metadata:
            print("Building Meta Structure")
            print('=======================')
            path = self.meta_entity_source_path
        else:
            print("Building Entity Structure")
            print('=========================')
            path = self.entity_source_path
            
        for x in os.listdir(path):
            tree = etree.parse(path + '/' + x)
            root = tree.getroot()
            root_type = root.tag.split("}")[1]
            if root_type == 'entity':
                self.entity_builder(metadata, root)
            if root_type == 'extension':
                self.entity_builder(metadata, root)
            if root_type == 'subtype':
                self.entity_builder(metadata, root)
            if root_type == 'delegate':
                self.entity_builder(metadata, root)
        return self

    def process_typelist(self, metadata: bool):
        path: str = ''
        if metadata:
            print("Building Typelist Meta Structure")
            print('================================')
            path = self.meta_typelist_source_path
        else:
            print("Building Typelist Structure")
            print('===========================')
            path = self.typelist_source_path

        for x in os.listdir(path):
            tree = etree.parse(path + '/' + x)
            root = tree.getroot()
            self.typelist_builder(metadata, root)
        return self

    def entity_builder(self, metadata: bool, root):
        root_type = root.tag.split("}")[1]
        if root_type == 'delegate':
            entity_name: str = root.attrib['name']
        elif root_type == 'extension':
            entity_name: str = root.attrib['entityName']
        else:
            entity_name: str = root.attrib['entity']
        print(f'{root_type}: {entity_name}')
        structure = self.find_plant_structure(entity_name)
        if structure.metadata == '':
            if metadata:
                structure.metadata = 'true'
            else:
                structure.metadata = 'false'
        if structure.type == '':
            structure.type = 'entity'
        if structure.stereotype == '':
            if metadata:
                structure.stereotype = "Base"
            else:
                structure.stereotype = 'Entity'
        if root_type == "subtype":
            structure.subtype = root.attrib['supertype']
            structure.type = 'subtype'
        if root_type == "delegate":
            structure.type = 'delegate'
            structure.stereotype = "Delegate"
        for component in root.iter():
            try:
                tag = component.tag.split("}")[1]
                if tag == 'column':
                    col_name = component.get("name")
                    col_type = component.get("type")
                    structure.add_column(col_name, col_type)
                if tag == 'implementsEntity':
                    implements_entity_name = component.get("name")
                    structure.add_implements_entity(implements_entity_name)
                if tag == 'array':
                    array_entity = component.get("arrayentity")
                    array_name = component.get("name")
                    self.remove_foreignkey_in_array(array_entity, entity_name)
                    structure.add_array(array_name, array_entity)
                if tag == 'typekey':
                    typekey_entity = component.get("typelist")
                    typekey_name = component.get("name")
                    structure.add_type_key(typekey_entity, typekey_name)
                if tag == 'foreignkey':
                    foreignkey_entity = component.get("fkentity")
                    foreignkey_name = component.get("name")
                    if not (self.foreignkey_in_array(foreignkey_entity, entity_name)):
                        structure.add_foreign_key(foreignkey_name, foreignkey_entity)
            except AttributeError:
                pass
        return self

    def typelist_builder(self, metadata: bool, root):
        typelist_name = root.attrib['name']
        print(f'typelist: {typelist_name}')
        structure = self.find_plant_structure(typelist_name, True)
        if structure.metadata == '':
            if metadata:
                structure.metadata = 'true'
            else:
                structure.metadata = 'false'
        if structure.stereotype == '':
            structure.stereotype = "Typelist"
        if structure.type == '':
            structure.type = 'typelist'
        if self.config_json['typelist_contents'] == 'true':
            for component in root.iter():
                try:
                    tag = component.tag.split("}")[1]
                    if tag == 'typecode':
                        code = component.get('code')
                        name = component.get('name')
                        structure.add_type_code(code, name)
                except:
                    pass

    def find_plant_structure(self, in_name, typelist: bool = False) -> PlantContent:
        for structure in self.plant_structures:
            if structure.name == in_name:
                if typelist and structure.type == 'typelist':
                    return structure
                if not typelist and not(structure.type == 'typelist'):
                    return structure
        structure = PlantContent()
        structure.name = in_name
        self.plant_structures.append(structure)
        return structure

    def foreignkey_in_array(self, foreignkey_entity: str, entity_name: str) -> bool:
        for structure in self.plant_structures:
            if structure.name == foreignkey_entity:
                if entity_name in structure.arrays.values():
                    return True
        return False

    def remove_foreignkey_in_array(self, array_entity: str, entity_name: str):
        for structure in self.plant_structures:
            if structure.name == array_entity:
                foreign_keys_copy = structure.foreign_keys.copy()
                for key, value in foreign_keys_copy.items():
                    if value == entity_name:
                        structure.foreign_keys.pop(key)
                        return

    def __init__(self, in_config_json):
        self.config_json = in_config_json
        self.plant_structures: list[PlantContent] = list()
        self.entity_source_path = self.config_json[
                                      'source_path'] + '/' + "modules/configuration/config/extensions/entity"
        self.delegate_source_path = self.config_json[
                                        'source_path'] + '/' + "modules/configuration/config/extensions/entity"
        self.typelist_source_path = self.config_json[
                                        'source_path'] + '/' + "modules/configuration/config/extensions/typelist"
        self.meta_entity_source_path = self.config_json[
                                           'source_path'] + '/' + "modules/configuration/config/metadata/entity"
        self.meta_delegate_source_path = self.config_json[
                                             'source_path'] + '/' + "modules/configuration/config/metadata/entity"
        self.meta_typelist_source_path = self.config_json[
                                             'source_path'] + '/' + "modules/configuration/config/metadata/typelist"
