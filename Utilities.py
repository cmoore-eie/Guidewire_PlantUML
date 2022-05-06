import PUMLTemplate
from PlantContent import PlantContent
from Cheetah.Template import Template


def find_plant_structure(plant_structures: list[PlantContent], in_name, enum: bool = False) -> PlantContent:
    for structure in plant_structures:
        if structure.name == in_name:
            if enum and structure.type == 'typelist':
                return structure
            if not enum and not (structure.type == 'typelist'):
                return structure
    structure = PlantContent()
    structure.name = in_name
    plant_structures.append(structure)
    return structure


def foreignkey_in_array(plant_structures: list[PlantContent], foreignkey_entity: str, entity_name: str) -> bool:
    """
    Before adding a foreign key a check is done to find if there is an array already defined. If an array is found
    the foreign key will not be created.
    """
    for structure in plant_structures:
        if structure.name == foreignkey_entity:
            if entity_name in structure.arrays.values():
                return True
    return False


def remove_foreignkey_in_array(plant_structures: list[PlantContent], array_entity: str, entity_name: str):
    """
    Identifies if there is a corresponding foreign key defined for the target entity in the array, if one is found it
    is removed to make sure that the relationship shown is only that of the array.
    """
    for structure in plant_structures:
        if structure.name == array_entity:
            foreign_keys_copy = structure.foreign_keys.copy()
            for key, value in foreign_keys_copy.items():
                if value == entity_name:
                    structure.foreign_keys.pop(key)
                    return


def build_template(template_name, namespace) -> str:
    if template_name == 'class':
        template_str = PUMLTemplate.get_class_template()
    elif template_name == 'delegate':
        template_str = PUMLTemplate.get_delegate_template()
    elif template_name == 'typelist':
        template_str = PUMLTemplate.get_typelist_template()
    elif template_name == 'implements':
        template_str = PUMLTemplate.get_implements_template()
    elif template_name == 'arrays':
        template_str = PUMLTemplate.get_array_template()
    elif template_name == 'typekeys':
        template_str = PUMLTemplate.get_typekeys_template()
    elif template_name == 'foreignkeys':
        template_str = PUMLTemplate.get_foreignkey_template()
    elif template_name == 'subtype':
        template_str = PUMLTemplate.get_subtype_template()

    template = Template(template_str, searchList=[namespace])
    return str(template)
