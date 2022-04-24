# Change Log

## 0.2.0

* Added support for full range of characters described in RFC (Kamyab Taghizadeh)

## 0.1.6

* Changed DictionaryClient.strategies and DictionaryClient.databases from instance attributes to read-only, lazy descriptors, so we don't incur the multiple network roundtrips if that data isn't needed.
