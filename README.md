# PhaazeDB
Database optimized for Phaaze working in a strange way.
JSON based requests DB.

Methods:

  select
    of:str, where:str, fields:list, offset:int, limit:int, store:str, join:dict

  update
    of:str, where:str, offset:int, limit:int, store:str, content:dict or str

  insert
    into:str, content:dict

  delete
    of:str, where:str, offset:int, limit:int, store:str

  create
    name:str

  drop
    name:str

  show
    recursive:bool, path:str

  default
    name:str, content:dict

  describe
    name:str

  option
    option:any, value:any

  import

  export
