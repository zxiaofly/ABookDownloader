def validate_file_name(file_name: str):
    file_name.strip()
    key_word = ['/', ':', '*', '?', '"', '<', '>', '|']
    file_name = str(file_name)
    original_file_name = file_name
    for word in key_word:
        file_name = file_name.replace(word, '')
    if file_name != original_file_name:
        file_name = file_name + "(Renamed)"
    return file_name