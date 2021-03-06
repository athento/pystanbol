def get_fields_by_entity(entities, fields):
    from components.enhancer.models import EntityAnnotation
    fields_metadata = {}
    if fields and len(fields) > 0:
        for ea in entities:
            if isinstance(ea, EntityAnnotation):
                entity = ea.entity
            else:
                entity = ea
            entity_metadata = []
            for field in fields:
                values = entity.values(field, localName=True)
                entity_metadata.extend(values)
            fields_metadata[entity.uri] = entity_metadata
    return fields_metadata


def get_ldpath_fields_by_entity(entities, prefixes, fields):
    built_fields = []
    for ldpath_field in fields: # Format of ldpath_field: foaf:depiction
        ldpath_field = ldpath_field.strip() # Remove spaces
        splitted = ldpath_field.split(':')
        prefix = splitted[0]
        field = splitted[1]
        try:
            namespace = prefixes[prefix]
        except KeyError:
            continue
        eproperty = namespace+field
        built_fields.append(eproperty)
    return get_fields_by_entity(entities, built_fields)
