def model_to_dict(model_instance):
    """
    Used to translate cqlengine.Model to dictionary
    so that it can be later translated to other models e.g. pydantic BaseModel
    TODO: how to map between cqlengine.Model and pydantic.BaseModel in an elegant way
    """
    result = {}
    for field_name, field in model_instance._columns.items():
        result[field_name] = getattr(model_instance, field_name)
    return result
