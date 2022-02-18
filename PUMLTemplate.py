def get_array_template() -> str:
    template = """
$Name *-- "$ArrayName" $ArrayType  """
    return template


def get_class_template() -> str:
    template = """
#set class_contents = $config_json['entity_contents'].lower()
#set ClassName = $structure.name
#set Stereotype = $structure.stereotype
##
class ${ClassName} <<${Stereotype}>> {
  #if $class_contents == 'true':
    #for key, value in $structure.columns.items():
  $key : $value
    #end for
  #end if
} 
"""
    return template


def get_delegate_template() -> str:
    template = """
#set delegate_contents = $config_json['delegate_contents'].lower()
#set DelegateName = $structure.name
#set Stereotype = $structure.stereotype
##
abstract ${DelegateName} <<${Stereotype}>> {
  #if $delegate_contents == 'true':
    #for key, value in $structure.columns.items():
  $key : $value
    #end for
  #end if
} 
"""
    return template


def get_foreignkey_template() -> str:
    template = """
$Name --> "$ForeignKeyName" $ForeignKeyType """
    return template


def get_implements_template() -> str:
    template = """
$Name ..> $ImplementsName """
    return template

def get_subtype_template() -> str:
    template = """
$structure.name --|> $structure.subtype """
    return template


def get_typekeys_template() -> str:
    template = """
$Name --> "$TypekeyName" $TypekeyType """
    return template


def get_typelist_template() -> str:
    template = """
#set typlist_contents = $config_json['typelist_contents'].lower()
#set TypelistName = $structure.name
#set Stereotype = $structure.stereotype
##
enum ${TypelistName} <<${Stereotype}>> {
  #if $typlist_contents == 'true':
    #for key, value in $structure.type_codes.items():
  $key
    #end for
  #end if
} 
"""
    return template
