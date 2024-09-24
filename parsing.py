def username(message):
    full_name = message.split(' ')
    if len(full_name) > 1:
        return ' '.join(full_name[1:])
    else:
        return ' '.join(full_name)
