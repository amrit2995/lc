import inflect
from spellchecker import SpellChecker
from helpers.common import UtilityClass


class WordProcessor:
    _spell_checker = SpellChecker()
    _inflect_engine = inflect.engine()
    _cache = {}

    @staticmethod
    def correct_spelling(word: str) -> str:
        if word in WordProcessor._cache:
            return WordProcessor._cache[word]
        
        correction = WordProcessor._spell_checker.correction(word)
        WordProcessor._cache[word] = correction if correction else word
        return WordProcessor._cache[word]

    @staticmethod
    def plural_to_singular(word: str) -> str:
        """Converts the given plural word into singular using inflect."""
        singular = WordProcessor._inflect_engine.singular_noun(word)
        UtilityClass.handleInfoLogs(f"Initial Word:{word} and Singular Word: {singular}")
        return singular if singular else word 

    @staticmethod
    def correct_and_singularize(word: str) -> str:
        corrected_word = WordProcessor.correct_spelling(word)
        singular_word = WordProcessor.plural_to_singular(corrected_word)
        return singular_word