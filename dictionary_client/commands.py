from functools import wraps


def dictionary_server_command(command_func):
    @wraps(command_func)
    def encodes_command(*args, **kwargs):
        command = command_func(*args, **kwargs)
        return f"{command}\r\n".encode("utf-8")

    return encodes_command


@dictionary_server_command
def show_strategies_command():
    return "SHOW STRAT"


@dictionary_server_command
def show_databases_command():
    return "SHOW DB"


@dictionary_server_command
def client_ident_command(client_id_info):
    return f"CLIENT {client_id_info}"


@dictionary_server_command
def disconnect_command():
    return "QUIT"


@dictionary_server_command
def define_word_command(word, db="*"):
    return f"DEFINE {db} {word}"


@dictionary_server_command
def match_command(word, db="*", strategy="exact"):
    return f"MATCH {db} {strategy} {word}"


@dictionary_server_command
def status_command():
    return "STATUS"


@dictionary_server_command
def show_info_command(db):
    return f"SHOW INFO {db}"


@dictionary_server_command
def show_server_command():
    return "SHOW SERVER"


@dictionary_server_command
def help_command():
    return "HELP"
