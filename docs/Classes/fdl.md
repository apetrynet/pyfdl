# FDL
The `FDL` class is meant to be an entry point and is a "merge" between a [Header](header.md) class and 
container class. The `Header` is created for you based on the arguments you provide at initialisation or 
you can pass a `Header` object as an attribute if you wish.  

::: pyfdl.FDL
    options:
        members: 
            - apply_defaults
            - check_required
            - validate
            - from_dict
            - to_dict
            - load_schema
            - header
