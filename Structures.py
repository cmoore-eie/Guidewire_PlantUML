import os
from PlantContent import PlantContent
import Utilities

from lxml import etree


def extract_tag_type(tag):
    if '}' in tag:
        return tag.split("}")[1]
    else:
        return tag


def extract_entity_name(root_type, attrib) -> str:
    if root_type == 'delegate':
        return attrib['name']
    elif root_type == 'extension':
        return attrib['entityName']
    else:
        return attrib['entity']


class GuidewireStructure:

    def build(self):
        print('')
        print('Building Entity Structures')
        print('==========================')
        self.process_entity(True)
        self.process_entity(False)
        print('\nBuilding Typelist Structures')
        print('============================')
        self.process_typelist(True)
        self.process_typelist(False)
        print('')
        print(f'{self.item_count} items processed')

    def process_entity(self, metadata: bool):
        if metadata:
            path = self.meta_entity_source_path
        else:
            path = self.entity_source_path

        print(path)

        for x in os.listdir(path):
            parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_comments=True)
            tree = etree.parse(path + '/' + x, parser)
            root = tree.getroot()
            if '}' in root.tag:
                root_type = root.tag.split("}")[1]
            else:
                root_type = root.tag
            if root_type == 'entity':
                self.entity_builder(metadata, root)
            if root_type == 'extension':
                self.entity_builder(metadata, root)
            if root_type == 'subtype':
                self.entity_builder(metadata, root)
            if root_type == 'delegate':
                self.entity_builder(metadata, root)
            self.item_count += 1
        return self

    def process_typelist(self, metadata: bool):
        if metadata:
            path = self.meta_typelist_source_path
        else:
            path = self.typelist_source_path

        print(path)

        for x in os.listdir(path):
            tree = etree.parse(path + '/' + x)
            root = tree.getroot()
            self.typelist_builder(metadata, root)
            self.item_count += 1
        return self

    def entity_builder(self, metadata: bool, root):
        root_type = extract_tag_type(root.tag)
        entity_name = extract_entity_name(root_type, root.attrib)
        structure = Utilities.find_plant_structure(self.plant_structures, entity_name)
        if root_type == 'extension':
            if structure.stereotype == 'Base':
                structure.stereotype = 'Base Extended'
            if structure.stereotype == 'Entity':
                structure.stereotype = 'Entity Extended'
        if 'type' in root.attrib.keys():
            if root.attrib['type'] == 'effdated' and not metadata:
                structure.stereotype = 'Effdated'
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
                tag = extract_tag_type(component.tag)
                match str(tag):
                    case 'column':
                        col_name = component.get("name")
                        col_type = component.get("type")
                        structure.add_column(col_name, col_type)
                    case 'monetaryamount':
                        col_name = component.get("name")
                        col_type = "monetaryamount"
                        structure.add_column(col_name, col_type)
                    case 'implementsEntity':
                        implements_entity_name = component.get("name")
                        structure.add_implements_entity(implements_entity_name)
                    case 'array':
                        array_entity = component.get("arrayentity")
                        array_name = component.get("name")
                        Utilities.remove_foreignkey_in_array(self.plant_structures, array_entity, entity_name)
                        structure.add_array(array_name, array_entity)
                    case 'typekey':
                        typekey_entity = component.get("typelist")
                        typekey_name = component.get("name")
                        structure.add_type_key(typekey_entity, typekey_name)
                    case 'foreignkey':
                        foreignkey_entity = component.get("fkentity")
                        foreignkey_name = component.get("name")
                        if not (Utilities.foreignkey_in_array(self.plant_structures, foreignkey_entity, entity_name)):
                            structure.add_foreign_key(foreignkey_name, foreignkey_entity)
                    case 'edgeForeignKey':
                        foreignkey_entity = component.get("fkentity")
                        foreignkey_name = component.get("name")
                        if not (Utilities.foreignkey_in_array(self.plant_structures, foreignkey_entity, entity_name)):
                            structure.add_foreign_key(foreignkey_name, foreignkey_entity)
            except AttributeError:
                pass
        return self

    def typelist_builder(self, metadata: bool, root):
        typelist_name = root.attrib['name']
        structure = Utilities.find_plant_structure(self.plant_structures, typelist_name, True)
        if structure.metadata == '':
            if metadata:
                structure.metadata = 'true'
            else:
                structure.metadata = 'false'
        if structure.stereotype == '':
            structure.stereotype = "Typelist"
        if structure.type == '':
            structure.type = 'typelist'
        if self.config_json['typelist_contents'].lower() == 'true':
            for component in root.iter():
                try:
                    tag = component.tag.split("}")[1]
                    if tag == 'typecode':
                        code = component.get('code')
                        name = component.get('name')
                        structure.add_type_code(code, name)
                except (AttributeError, IndexError):
                    pass

    def __init__(self, in_config_json):
        self.item_count = 0
        self.config_json = in_config_json
        self.plant_structures: list[PlantContent] = list()
        source_path = self.config_json['source_path']
        self.entity_source_path = source_path + '/' + "modules/configuration/config/extensions/entity"
        self.delegate_source_path = source_path + '/' + "modules/configuration/config/extensions/entity"
        self.typelist_source_path = source_path + '/' + "modules/configuration/config/extensions/typelist"
        self.meta_entity_source_path = source_path + '/' + "modules/configuration/config/metadata/entity"
        self.meta_delegate_source_path = source_path + '/' + "modules/configuration/config/metadata/entity"
        self.meta_typelist_source_path = source_path + '/' + "modules/configuration/config/metadata/typelist"
