import os
from lxml import etree

core_entities = []

class BuildTypes:
    entity_types = dict()
    typelist_types = dict()
    delegate_types = dict()
    meta_entity_types = dict()
    meta_typelist_types = dict()
    meta_delegate_types = dict()

    def type_builder(self):
        print("")
        print("Processing Entities")
        print("===================")
        for x in os.listdir(self.entity_source_path):
            tree = etree.parse(self.entity_source_path + '/' + x)
            root = tree.getroot()

    def extensions_builder(self):
        print("")
        print("Processing Extensions")
        print("=====================")
        for x in os.listdir(self.entity_source_path):
            if self.process_item(x):
                tree = etree.parse(self.entity_source_path + '/' + x)
                root = tree.getroot()
                root_type = root.tag.split("}")[1]
                if root_type == 'entity':
                    print(f'entity : {x}')
                    self.entity_types[x] = root
                if root_type == 'subtype':
                    print(f'subtype : {x}')
                    self.entity_types[x] = root
                if root_type == 'delegate':
                    print(f'delegate : {x}')
                    self.delegate_types[x] = root
        for x in os.listdir(self.typelist_source_path):
            if self.process_item(x):
                print(f'typelist : {x}')
                tree = etree.parse(self.typelist_source_path + '/' + x)
                root = tree.getroot()
                self.typelist_types[x] = root
        self.typelist_builder(False, self.typelist_types)
        self.delegate_builder(False, self.delegate_types)
        self.entity_builder(False, self.entity_types)
        return self

    def meta_builder(self):
        print("")
        print("Processing Metadata")
        print("===================")
        for x in os.listdir(self.meta_entity_source_path):
            if self.process_item(x):
                tree = etree.parse(self.meta_entity_source_path + '/' + x)
                root = tree.getroot()
                root_type = root.tag.split("}")[1]
                if root_type == 'entity':
                    print(f'entity : {x}')
                    self.meta_entity_types[x] = root
                if root_type == 'subtype':
                    print(f'subtype : {x}')
                    self.meta_entity_types[x] = root
                if root_type == 'delegate':
                    print(f'delegate : {x}')
                    self.meta_delegate_types[x] = root
        for x in os.listdir(self.meta_typelist_source_path):
            if self.process_item(x):
                print(f'typelist : {x}')
                tree = etree.parse(self.meta_typelist_source_path + '/' + x)
                root = tree.getroot()
                self.meta_typelist_types[x] = root
        self.typelist_builder(True, self.meta_typelist_types)
        self.delegate_builder(True, self.meta_delegate_types)
        self.entity_builder(True, self.meta_entity_types)
        return self

    def entity_builder(self, metadata : bool, in_types):
        entity_file_name = self.target_path
        uml_name = ''
        steryotype = ''
        class_colour = ''
        if metadata:
            entity_file_name = entity_file_name + "/BaseEntity.puml"
            uml_name = 'BaseEntity'
            steryotype = 'Base'
            class_colour = self.config_json['meta_entity_colour']
        else:
            entity_file_name = entity_file_name + "/ExtensionEntity.puml"
            uml_name = 'ExtensionEntity'
            steryotype = 'Entity'
            class_colour = self.config_json['entity_colour']
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
        file.write(f'\tBackgroundColor<<{steryotype}>> {class_colour}\n')
        file.write('}\n')
        file.write('\n')
        for entity in in_types:
            root = in_types[entity]
            root_type = root.tag.split("}")[1]
            entity_name = entity.replace('.eti', '')
            file.write(f'class {entity_name} <<{steryotype}>>' + ' {\n')
            for att in root.iter():
                try:
                    tag = att.tag.split("}")[1]
                    if tag == 'column':
                        col_name = att.get("name")
                        col_type = att.get("type")
                        file.write(f'\t{col_name} : {col_type}\n')
                except:
                    pass
            file.write('} \n')
            for att in root.iter():
                try:
                    tag = att.tag.split("}")[1]
                    if tag == 'implementsEntity':
                        col_name = att.get("name")
                        if self.process_item(col_name):
                          file.write(f'{entity_name} ..> {col_name}\n')
                    if tag == 'array':
                        array_entity = att.get("arrayentity")
                        array_name = att.get("name")
                        if self.process_item(array_entity):
                          file.write(f'{entity_name} *-- "{array_name}" {array_entity}\n')
                    if tag == 'typekey':
                        typekey_entity = att.get("typelist")
                        typekey_name = att.get("name")
                        if self.process_item(array_entity):
                          file.write(f'{entity_name} --> "{typekey_name}" {typekey_entity}\n')
                    if tag == 'foreignkey':
                        fkentity = att.get("fkentity")
                        name = att.get("name")
                        if self.process_item(fkentity):
                          file.write(f'{entity_name} --> "{name}" {fkentity}\n')
                except:
                    pass
            if root_type == "subtype":
                parent = root.attrib['supertype']
                file.write(f'{entity_name} --|> "{parent}"\n')
            file.write("\n")
        file.write("@enduml\n")
        file.close()
        return self

    def delegate_builder(self, metadata : bool, in_types):
        delegate_file_name = self.target_path + "/BaseDelegate.puml"
        delegate_file_name = self.target_path
        uml_name = ''
        steryotype = ''
        class_colour = ''
        if metadata:
            delegate_file_name = delegate_file_name + "/BaseDelegate.puml"
            uml_name = 'BaseDelegate'
            class_colour = self.config_json['delegate_colour']
        else:
            delegate_file_name = delegate_file_name + "/ExtensionDelegate.puml"
            uml_name = 'ExtensionDelegate'
            class_colour = self.config_json['delegate_colour']
        file = open(delegate_file_name, 'w')
        file.write(f"@startuml {uml_name}\n")
        file.write('skinparam class {\n')
        file.write(f'\tBackgroundColor<<Delegate>> {class_colour}\n')
        file.write('}\n')
        file.write('\n')
        for delegate in in_types:
            root = in_types[delegate]
            delegate_name = delegate.replace('.eti', '')
            file.write(f'abstract {delegate_name} <<Delegate>>' + ' {\n')
            for att in root.iter():
                try:
                    tag = att.tag.split("}")[1]
                    if tag == 'column':
                        col_name = att.get("name")
                        col_type = att.get("type")
                        file.write(f'\t{col_name} : {col_type}\n')
                except:
                    pass
            for att in root.iter():
                try:
                    tag = att.tag.split("}")[1]
                    if tag == 'implementsEntity':
                        col_name = att.get("name")
                        if self.process_item(col_name):
                          file.write(f'{delegate_name} ..> {col_name}\n')
                    if tag == 'array':
                        array_entity = att.get("arrayentity")
                        array_name = att.get("name")
                        if self.process_item(array_entity):
                          file.write(f'{delegate_name} *-- "{array_name}" {array_entity}\n')
                    if tag == 'typekey':
                        typekey_entity = att.get("typelist")
                        typekey_name = att.get("name")
                        if self.process_item(array_entity):
                          file.write(f'{delegate_name} --> "{typekey_name}" {typekey_entity}\n')
                    if tag == 'foreignkey':
                        fkentity = att.get("fkentity")
                        name = att.get("name")
                        if self.process_item(fkentity):
                          file.write(f'{delegate_name} --> "{name}" {fkentity}\n')
                except:
                    pass
            file.write('} \n\n')
        file.write("@enduml\n")
        file.close()
        return self

    def typelist_builder(self, metadata : bool, in_types):
        entity_file_name = self.target_path
        uml_name = ''
        if metadata:
            entity_file_name = entity_file_name + "/BaseTypelist.puml"
            uml_name = 'BaseTypelists'
        else:
            entity_file_name = entity_file_name + "/ExtensionTypelist.puml"
            uml_name = 'ExtensionTypelist'
        file = open(entity_file_name, 'w')
        file.write(f"@startuml {uml_name}\n\n")
        file.write('skinparam enum {\n')
        file.write(f'\tBackgroundColor<<Typelist>> {self.config_json["typelist_colour"]}\n')
        file.write('}\n')
        file.write('\n')
        for entity in in_types:
            root = in_types[entity]
            typelist_name = entity.replace('.tti', '')
            file.write(f'enum {typelist_name} <<Typelist>>' + ' {\n')
            if self.config_json['typelist_contents'] == 'true':
              for att in root.iter():
                try:
                    tag = att.tag.split("}")[1]
                    if tag == 'typecode':
                        typecode_code = att.get("code")
                        file.write(f'\t{typecode_code}\n')
                except:
                    pass
            file.write('} \n\n')
        file.write("@enduml\n")
        file.close()
        return self

    def process_item(self, in_item_name):
        if in_item_name.find('.ttx') >= 0:
            return False
        elif in_item_name.find('.etx') >= 0:
            return False
        elif in_item_name.find('.tix') >= 0:
            return False
        name = in_item_name.split('.')[0]
        process = False
        if self.config_json['include_custom'] == 'true':
            if in_item_name.find(self.config_json['custom_prefix']) >= 0:
                return True
        if self.core_only == 'true':
            if name in core_entities:
                process = True
        else:
            process = True
        return process

    def __init__(self, in_config_json):
        self.config_json = in_config_json
        self.entity_source_path = self.config_json['source_path'] + '/' + "modules/configuration/config/extensions/entity"
        self.delegate_source_path = self.config_json['source_path'] + '/' + "modules/configuration/config/extensions/entity"
        self.typelist_source_path = self.config_json['source_path'] + '/' + "modules/configuration/config/extensions/typelist"
        self.meta_entity_source_path = self.config_json['source_path'] + '/' + "modules/configuration/config/metadata/entity"
        self.meta_delegate_source_path = self.config_json['source_path'] + '/' + "modules/configuration/config/metadata/entity"
        self.meta_typelist_source_path = self.config_json['source_path'] + '/' + "modules/configuration/config/metadata/typelist"
        self.target_path = self.config_json['target_path']
        self.core_only = self.config_json['core_only']
        for entity in self.config_json["core_entities"]:
            core_entities.append(entity["core_entity"])
