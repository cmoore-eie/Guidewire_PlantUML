from PlantContent import PlantContent

def find_plant_structure(plant_structures: list[PlantContent], in_name, enum: bool = False) -> PlantContent:
    for structure in plant_structures:
        if structure.name == in_name:
            if enum and structure.type == 'typelist':
                return structure
            if not enum and not(structure.type == 'typelist'):
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
    Identifies if there is a corrisponding foreign key defined for the target entity in the arrray, if one is found it
    is removed to make sure that the relationship shown is only that of the array.
    """    
    for structure in plant_structures:
        if structure.name == array_entity:
            foreign_keys_copy = structure.foreign_keys.copy()
            for key, value in foreign_keys_copy.items():
                if value == entity_name:
                    structure.foreign_keys.pop(key)
                    return
