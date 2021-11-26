# Change Log

## 0.1.6

* Changed DictionaryClient.strategies and DictionaryClient.databases from instance attributes to read-only, lazy descriptors, so we don't incur the multiple network roundtrips if that data isn't needed.
