import unittest

from dictionary_client.word import (
    ATOM,
    DQABLE,
    DQSTRING,
    SQABLE,
    SQSTRING,
    Word,
)


class TestUtils(unittest.TestCase):
    def test_regexes(self):
        self.assertIsNotNone(ATOM.match("word"))
        self.assertIsNotNone(ATOM.match("کلمه"))
        self.assertIsNotNone(ATOM.match("ワード"))
        self.assertIsNone(ATOM.match("word group"))
        self.assertIsNone(ATOM.match("word's"))
        self.assertIsNone(ATOM.match('"word"'))
        self.assertIsNone(ATOM.match("word\\"))

        self.assertIsNotNone(DQABLE.match("word"))
        self.assertIsNotNone(DQABLE.match("word group"))
        self.assertIsNotNone(DQABLE.match("word's"))
        self.assertIsNotNone(DQABLE.match("کلمه"))
        self.assertIsNotNone(DQABLE.match("کلمه ها"))
        self.assertIsNotNone(DQABLE.match("ワード"))
        self.assertIsNotNone(DQABLE.match("ワ ー ド"))
        self.assertIsNone(DQABLE.match('"word"'))
        self.assertIsNotNone(DQSTRING.match('"word"'))

        self.assertIsNotNone(SQABLE.match("word"))
        self.assertIsNotNone(SQABLE.match('word"s'))
        self.assertIsNotNone(SQABLE.match("word group"))
        self.assertIsNotNone(SQABLE.match("کلمه"))
        self.assertIsNotNone(SQABLE.match("کلمه ها"))
        self.assertIsNotNone(SQABLE.match("ワード"))
        self.assertIsNotNone(SQABLE.match("ワ ー ド"))
        self.assertIsNone(SQABLE.match("word's"))
        self.assertIsNotNone(SQSTRING.match("'word'"))

    def test_format(self):
        self.assertEqual(str(Word("word")), "word")
        self.assertEqual(str(Word("'word'")), "'word'")
        self.assertEqual(str(Word('"word"')), '"word"')
        self.assertEqual(str(Word("'")), '"\'"')
        self.assertEqual(str(Word('"')), "'\"'")
        self.assertEqual(str(Word("\\")), '"\\"')

        with self.assertRaises(ValueError):
            Word("""\\"'""")
