def encode_query(query, encoding='utf-8'):
    return f'{query}\r\n'.encode(encoding)

def show_strategies_command():
    return encode_query('SHOW STRATEGIES')

def client_ident_command(client_id_info):
    return encode_query(f'CLIENT {client_id_info}')


def disconnect_command():
    return encode_query('QUIT')


def define_word_command(word, db='*'):
    return encode_query(f'DEFINE {db} {word}')
