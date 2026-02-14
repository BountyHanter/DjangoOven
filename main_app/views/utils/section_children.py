def get_section_with_children(section):
    result = [section]

    children = section.children.filter(is_active=True)

    for child in children:
        result.extend(get_section_with_children(child))

    return result
