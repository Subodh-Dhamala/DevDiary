entries = []


def create_entry(entry_data):
    new_entry = {
        "id": len(entries) + 1,
        "title": entry_data.title,
        "content": entry_data.content
    }

    entries.append(new_entry)
    return new_entry


def get_all_entries():
    return entries


def get_entry_by_id(entry_id):
    for entry in entries:
        if entry["id"] == entry_id:
            return entry

    return None


def update_entry(entry_id, entry_data):
    entry = get_entry_by_id(entry_id)

    if entry is None:
        return None

    if entry_data.title is not None:
        entry["title"] = entry_data.title

    if entry_data.content is not None:
        entry["content"] = entry_data.content

    return entry


def delete_entry(entry_id):
    for index, entry in enumerate(entries):
        if entry["id"] == entry_id:
            return entries.pop(index)

    return None