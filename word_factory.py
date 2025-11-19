from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

from word_classes import NaviWord, NaviNoun, NaviVerb, NaviPronoun, NaviAdjective, NaviNumber, NaviParticle, NaviPrenoun
from navi_errors import WordClassificationError


class WordClassificationContext:
    """Context for word classification"""
    
    def __init__(self, word: str, position: int, all_words: List[str]):
        self.word = word
        self.position = position
        self.all_words = all_words
        self.previous_word = all_words[position - 1] if position > 0 else None
        self.next_word = all_words[position + 1] if position < len(all_words) - 1 else None


class WordClassifier(ABC):
    """Abstract base class for word classifiers"""

    # Classify a word and return appropriate word object
    @abstractmethod
    def classify(self, word: str, position: int) -> Optional[NaviWord]:
        pass
    # Check if this classifier can handle the given word
    @abstractmethod
    def can_classify(self, word: str) -> bool:
        pass


class ParticleClassifier(WordClassifier):
    """Classifier for particles"""
    
    def __init__(self):
        self.particles = {
            'srak': 'question',
            'kefyak': 'question',
            'pe': 'question',
            'pefnel': 'question',
            'pehem': 'question',
            'pehrr': 'question',
            'ma': 'vocative',
            'sì': 'conjunction',
            'ulte': 'conjunction',
            'fu': 'conditional',
            'to': 'conditional',
            'nang': 'negative',
            'srane': 'affirmative',
            'kehe': 'negative',
            'o': 'exclamative',
            'au': 'exclamative'
        }
    
    def can_classify(self, word: str) -> bool:
        return word.lower() in self.particles
    
    def classify(self, word: str, position: int) -> Optional[NaviParticle]:
        word_lower = word.lower()
        if word_lower in self.particles:
            return NaviParticle(word, position, self.particles[word_lower])
        return None


class NumberClassifier(WordClassifier):
    """Classifier for numbers"""
    
    def __init__(self):
        self.numbers = {
            "'aw": 1, "mune": 2, "pxey": 3, "tsing": 4,
            "mrr": 5, "pukap": 6, "kinä": 7, "vol": 8
        }
    
    def can_classify(self, word: str) -> bool:
        return word.lower() in self.numbers
    
    def classify(self, word: str, position: int) -> Optional[NaviNumber]:
        word_lower = word.lower()
        if word_lower in self.numbers:
            return NaviNumber(word, position, self.numbers[word_lower])
        return None


class NounClassifier(WordClassifier):
    """Classifier for nouns"""
    
    def __init__(self):
        # Common Na'vi nouns with characteristics
        self.nouns = {
            'utral': {'gender': 'neutral', 'ends_with_vowel': True},
            'tsmukan': {'gender': 'male', 'ends_with_vowel': False},
            'tsmuke': {'gender': 'female', 'ends_with_vowel': False},
            'tìrey': {'gender': 'neutral', 'ends_with_vowel': True},
            'kelku': {'gender': 'neutral', 'ends_with_vowel': True},
            'pxun': {'gender': 'neutral', 'ends_with_vowel': False},
            'atan': {'gender': 'neutral', 'ends_with_vowel': False},
            'samsiyu': {'gender': 'neutral', 'ends_with_vowel': True},
            'iknimaya': {'gender': 'neutral', 'ends_with_vowel': True},
            'hrrap': {'gender': 'neutral', 'ends_with_vowel': False}
        }
    
    def can_classify(self, word: str) -> bool:
        return word.lower() in self.nouns
    
    def classify(self, word: str, position: int) -> Optional[NaviNoun]:
        word_lower = word.lower()
        if word_lower in self.nouns:
            characteristics = self.nouns[word_lower]
            return NaviNoun(
                word, position,
                case="subjective",
                number="singular",
                gender=characteristics['gender'],
                ends_with_vowel=characteristics['ends_with_vowel'],
                ends_with_diphthong=self._ends_with_diphthong(word_lower)
            )
        return None
    
    def _ends_with_diphthong(self, word: str) -> bool:
        diphthongs = ['aw', 'ew', 'ay', 'ey', 'oy', 'uy']
        return any(word.endswith(diph) for diph in diphthongs)


class VerbClassifier(WordClassifier):
    """Classifier for verbs"""
    
    def __init__(self):
        # Common Na'vi verbs
        self.verbs = {
            'taron': {'transitivity': 'transitive'},
            'kameie': {'transitivity': 'transitive'},
            'tìng': {'transitivity': 'intransitive'},
            'za\'u': {'transitivity': 'intransitive'},
            'kä': {'transitivity': 'intransitive'},
            'oe': {'transitivity': 'intransitive'},
            'tul': {'transitivity': 'intransitive'},
            'hahaw': {'transitivity': 'intransitive'},
            'fpe\'o': {'transitivity': 'transitive'},
            'tìng': {'transitivity': 'intransitive'},
            'sivar': {'transitivity': 'intransitive'},
            'yom': {'transitivity': 'transitive'},
            'tswayon': {'transitivity': 'transitive'}
        }
    
    def can_classify(self, word: str) -> bool:
        # Remove infixes for checking
        clean_word = self._remove_infixes(word.lower())
        return clean_word in self.verbs
    
    def classify(self, word: str, position: int) -> Optional[NaviVerb]:
        clean_word = self._remove_infixes(word.lower())
        if clean_word in self.verbs:
            characteristics = self.verbs[clean_word]
            return NaviVerb(
                word, position,
                transitivity=characteristics['transitivity'],
                is_compound=self._is_compound(word)
            )
        return None
    
    def _remove_infixes(self, word: str) -> str:
        # Simple infix removal 
        import re
        # Remove content between < and >
        return re.sub(r'<[^>]*>', '', word)
    
    def _is_compound(self, word: str) -> bool:
        # Check if word appears to be compound 
        return '-' in word or len(word) > 8


class PrenounClassifier(WordClassifier):
    """Classifier for prenoun"""
    
    def __init__(self):
        self.prenouns = {
            'fì': 'deictic',
            'tsa': 'deictic',
            'fra': 'relative',
            'pe': 'interrogative',
            'fay': 'negative',
            'fayl': 'negative',
            'taw': 'demonstrative'
        }
    
    def can_classify(self, word: str) -> bool:
        return word.lower() in self.prenouns
    
    def classify(self, word: str, position: int) -> Optional[NaviPrenoun]:
        word_lower = word.lower()
        if word_lower in self.prenouns:
            return NaviPrenoun(word, position, self.prenouns[word_lower])
        return None


class AdjectiveClassifier(WordClassifier):
    """Classifier for adjectives"""
    
    def __init__(self):
        self.adjectives = {
            'sìltsan': {'is_color': False},
            'kaltxì': {'is_color': False},
            'lor': {'is_color': False},
            'ean': {'is_color': False},
            'txep': {'is_color': False},
            'nìaw': {'is_color': False},
            'nìawve': {'is_color': False},
            'rit': {'is_color': False},
            'tstxen': {'is_color': False},
            'hìn': {'is_color': False},
            'ehu': {'is_color': True},
            'puk': {'is_color': True},
            'titin': {'is_color': True},
            'kllkxik': {'is_color': True},
            'fpam': {'is_color': True},
            'srr': {'is_color': True},
            'unil': {'is_color': True},
            'teng': {'is_color': True},
            'kxam': {'is_color': True}
        }
    
    def can_classify(self, word: str) -> bool:
        return word.lower() in self.adjectives
    
    def classify(self, word: str, position: int) -> Optional[NaviAdjective]:
        word_lower = word.lower()
        if word_lower in self.adjectives:
            characteristics = self.adjectives[word_lower]
            return NaviAdjective(
                word, position,
                derived_with_le=word_lower.startswith('le'),
                is_color=characteristics['is_color']
            )
        return None


class PronounClassifier(WordClassifier):
    """Classifier for pronouns"""
    
    def __init__(self):
        self.pronouns = {
            'oe': {'person': 'first', 'number': 'singular', 'animacy': 'animate'},
            'oel': {'person': 'first', 'number': 'singular', 'animacy': 'animate'},
            'nga': {'person': 'second', 'number': 'singular', 'animacy': 'animate'},
            'ngati': {'person': 'second', 'number': 'singular', 'animacy': 'animate'},
            'po': {'person': 'third', 'number': 'singular', 'animacy': 'animate'},
            'fo': {'person': 'third', 'number': 'plural', 'animacy': 'animate'},
            'moe': {'person': 'first', 'number': 'dual', 'animacy': 'animate'},
            'menga': {'person': 'second', 'number': 'dual', 'animacy': 'animate'},
            'mefo': {'person': 'third', 'number': 'dual', 'animacy': 'animate'},
            'ayoeng': {'person': 'first', 'number': 'plural', 'animacy': 'animate', 'inclusivity': 'inclusive'},
            'aynga': {'person': 'second', 'number': 'plural', 'animacy': 'animate'},
            'ayfo': {'person': 'third', 'number': 'plural', 'animacy': 'animate'},
            'fko': {'person': 'third', 'number': 'singular', 'animacy': 'animate'},
            'tsaw': {'person': 'third', 'number': 'singular', 'animacy': 'inanimate'}
        }
    
    def can_classify(self, word: str) -> bool:
        return word.lower() in self.pronouns
    
    def classify(self, word: str, position: int) -> Optional[NaviPronoun]:
        word_lower = word.lower()
        if word_lower in self.pronouns:
            characteristics = self.pronouns[word_lower]
            return NaviPronoun(
                word, position,
                case="subjective",
                person=characteristics['person'],
                number=characteristics['number'],
                animacy=characteristics['animacy'],
                inclusivity=characteristics.get('inclusivity', 'exclusive'),
                gender='neutral'
            )
        return None


class NaviWordFactory:
    """Factory for creating Na'vi word objects"""
    
    def __init__(self):
        self.classifiers = [
            ParticleClassifier(),
            NumberClassifier(),
            PrenounClassifier(),
            PronounClassifier(),
            AdjectiveClassifier(),
            VerbClassifier(),
            NounClassifier()
        ]
    # Create a word object using appropriate classifier
    def create_word(self, word: str, position: int) -> NaviWord:
        for classifier in self.classifiers:
            if classifier.can_classify(word):
                result = classifier.classify(word, position)
                if result:
                    return result
        
        # Default to noun if no classifier matches
        return NaviNoun(word, position, case="subjective", number="singular")

# Context-aware word factory that considers surrounding words
class ContextAwareWordFactory(NaviWordFactory):
    
    def create_word_from_context(self, context: WordClassificationContext) -> NaviWord:
        """Create word using context information"""
        word = context.word
        position = context.position
        
        # Special handling for vocative particles
        if word.lower() == 'ma' and context.next_word:
            # If "ma" is followed by a noun, it's likely vocative
            next_lower = context.next_word.lower()
            if any(next_lower == noun for noun in ['tsmukan', 'tsmuke', 'tute', 'tute']):
                particle = ParticleClassifier().classify(word, position)
                if particle:
                    return particle
        
        # Use parent factory for general classification
        return self.create_word(word, position)


