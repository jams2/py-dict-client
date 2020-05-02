def encode_query(query, encoding="utf-8"):
    return f"{query}\r\n".encode(encoding)


def show_strategies_command():
    return encode_query("SHOW STRAT")


def show_databases_command():
    return encode_query("SHOW DB")


def client_ident_command(client_id_info):
    return encode_query(f"CLIENT {client_id_info}")


def disconnect_command():
    return encode_query("QUIT")


def define_word_command(word, db="*"):
    return encode_query(f"DEFINE {db} {word}")


def match_command(word, db="*", strategy="exact"):
    return encode_query(f"MATCH {db} {strategy} {word}")
