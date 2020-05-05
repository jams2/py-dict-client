

# py-dict-client

`py-dict-client` is a Python 3 client implementing the [Dictionary Server Protocol](https://tools.ietf.org/html/rfc2229).


## Usage

    >>> from dictionary_client import DictionaryClient
    >>> dc = DictionaryClient()
    
    >>> dc.databases
    {'fra-eng': 'French-English FreeDict Dictionary ver. 0.4.1',
     'eng-fra': 'English-French FreeDict Dictionary ver. 0.1.6',
     'wn': 'WordNet (r) 3.1 (2011)',
     'foldoc': 'The Free On-line Dictionary of Computing (2020-04-05)'}
    
    >>> dc.define('oiseau', db='fra-eng').content
    [{'db': 'fra-eng', 'definition': 'oiseau /wazo/ <n, masc>\nbird'}]
    
    >>> dc.define('chauffeur').content
    [{'db': 'fra-eng', 'definition': 'chauffeur /ʃofœʀ/ <n, masc>\nchauffeur, driver'},
     {'db': 'eng-fra', 'definition': 'chauffeur /ʃoufər/\nchauffeur'},
     {'db': 'wn', 'definition': 'chauffeur\n    n 1: a man paid to drive a privately owned car\n...'}]
    
    >>> dc.match('hello').content
    defaultdict(<class 'list'>, {'eng-fra': ['hello'], 'wn': ['hello'], 'foldoc': ['hello']})
    
    >>> dc.disconnect()


## TODO implement remaining commands in specification 

-   [X] STATUS
-   [X] SHOW INFO
-   [X] SHOW SERVER
-   [X] HELP
-   [ ] OPTION
-   [ ] AUTH
-   [ ] SASLAUTH

