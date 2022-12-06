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
        self.table: str = ''
        self.columns: dict[str, str] = dict()
        self.arrays: dict[str, str] = dict()
        self.implements_entities: dict[str, str] = dict()
        self.foreign_keys: dict[str, str] = dict()
        self.type_keys: dict[str, str] = dict()
        self.type_codes: dict[str, str] = dict()
