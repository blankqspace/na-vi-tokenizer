import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

class NaviWord(ABC):
    
    def __init__(self, text: str, position: int = 0):
        self.text = text
        self.position = position
        self.normalized = text.lower().strip()
        self._validate_word()
    
    @abstractmethod
    def get_word_type(self) -> str:
        pass
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        return {
            'text': self.text,
            'position': self.position,
            'word_type': self.get_word_type(),
            'normalized': self.normalized
        }
    
    def _validate_word(self) -> None:
        if not self.text:
            raise ValueError("Word text cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        return bool(re.match(r"^[a-zA-ZàèìòùÀÈÌÒÙäëïöüÄËÏÖÜ\'-]+$", self.text))
    
    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.text}', pos={self.position})"


class DeclinableWord(NaviWord): # for nouns and pronouns
    
    def __init__(self, text: str, position: int = 0, case: str = "subjective"):
        super().__init__(text, position)
        self.case = case
        self._case_endings = self._initialize_case_endings()
    
    @abstractmethod
    def _initialize_case_endings(self) -> Dict[str, str]:
        pass
    
    def get_case(self, case: str) -> str:
        if case not in self._case_endings:
            raise ValueError(f"Unknown case: {case}")
        return self.text + self._case_endings[case]
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info['case'] = self.case
        return info


class InflectableWord(NaviWord): # for verbs and adjectives
    
    def __init__(self, text: str, position: int = 0):
        super().__init__(text, position)
        self._infixed_form = None
    
    @abstractmethod
    def apply_inflection(self, **kwargs) -> str:
        pass
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        if self._infixed_form:
            info['infixed_form'] = self._infixed_form
        return info


class NaviNoun(DeclinableWord):
    
    def __init__(
        self,
        text: str,
        position: int = 0,
        case: str = "subjective",
        number: str = "singular",
        gender: str = "neutral",
        ends_with_vowel: bool = True,
        ends_with_diphthong: bool = False,
        ends_with_pseudovowel: bool = False,
    ):
        self.number = number
        self.gender = gender
        self.ends_with_vowel = ends_with_vowel
        self.ends_with_diphthong = ends_with_diphthong
        self.ends_with_pseudovowel = ends_with_pseudovowel
        self._lenition_applied = False
        
        super().__init__(text, position, case)
    
    def get_word_type(self) -> str:
        return "noun"
    
    def _initialize_case_endings(self) -> Dict[str, str]:
        return {
            "subjective": "",
            "agentive": self._get_agentive(),
            "patientive": self._get_patientive(),
            "dative": self._get_dative(),
            "genitive": self._get_genitive(),
            "topical": self._get_topical(),
        }
    
    def _get_agentive(self) -> str:
        return "l" if self.ends_with_vowel else "il"
    
    def _get_patientive(self) -> str:
        return "ti" if (self.ends_with_vowel or self.ends_with_diphthong) else "it"
    
    def _get_dative(self) -> str:
        return "ru" if (self.ends_with_vowel or self.ends_with_diphthong) else "ur"
    
    def _get_genitive(self) -> str:
        if self.ends_with_vowel:
            if self.text.endswith(("o", "u")):
                return "ä"
            return "yä"
        return "ä"
    
    def _get_topical(self) -> str:
        return "ri" if self.ends_with_vowel else "iri"
    
    def get_number(self, number: str) -> str:
        """Get noun in specified number with proper lenition"""
        number_prefixes = {"singular": "", "dual": "me", "trial": "pxe", "plural": "ay"}
        prefix = number_prefixes.get(number, "")
        
        if prefix:
            # Special case for "utral" 
            if self.text == "utral":
                if number == "dual":
                    return "mutral"
                elif number == "plural":
                    return "autral"
            
            lenited_base = self._apply_lenition(self.text)
            self._lenition_applied = True
            return prefix + lenited_base
        return self.text
    
    def get_number_with_case(self, number: str, case: str) -> str: # noun - number + case
        
        numbered_form = self.get_number(number)
        temp_noun = NaviNoun(numbered_form, case=case)
        return temp_noun.get_case(case)
    
    def _apply_lenition(self, word: str) -> str:

        lenition_rules = {
            "px": "p", "tx": "t", "kx": "k",
            "p": "f", "t": "s", "k": "h",
            "ts": "s"
        }
        
        for from_sound, to_sound in lenition_rules.items():
            if word.startswith(from_sound):
                return to_sound + word[len(from_sound):]
        return word
    
    def make_indefinite(self) -> str:
        return self.text + "o"
    
    @property
    def has_lenition(self) -> bool:
        return self._lenition_applied
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info.update({
            'case' : self.case, 
            'number': self.number,
            'gender': self.gender,
            'ends_with_vowel': self.ends_with_vowel,
            'ends_with_diphthong': self.ends_with_diphthong,
            'has_lenition': self.has_lenition
        })
        return info


class NaviPronoun(DeclinableWord):
    
    def __init__(
        self,
        text: str,
        position: int = 0,
        case: str = "subjective",
        person: str = "third",
        number: str = "singular",
        animacy: str = "animate",
        inclusivity: str = "exclusive",
        gender: str = "neutral",
        is_honorific: bool = False,
    ):
        self.person = person
        self.number = number
        self.animacy = animacy
        self.inclusivity = inclusivity
        self.gender = gender
        self.is_honorific = is_honorific
        
        super().__init__(text, position, case)
    
    def get_word_type(self) -> str:
        return "pronoun"
    
    def _initialize_case_endings(self) -> Dict[str, str]:
        # Pronouns follow same case rules as nouns ending in vowels
        temp_noun = NaviNoun(self.text, ends_with_vowel=True)
        return temp_noun._initialize_case_endings()
    
    def get_genitive(self) -> str:
        """Get genitive form with irregular forms"""
        irregular_genitives = {
            "fko": "fkeyä", "nga": "ngeyä", "po": "peyä",
            "sno": "sneyä", "tsa'u": "tseyä", "fo": "feyä",
            "awnga": "awngeyä", "ayoeng": "ayoengeyä",
            "oe": "oeyä", "moe": "moeyä", "pxoe": "pxoeyä",
            "ayoe": "ayoeyä", "oeng": "oengeyä", "pxoeng": "pxoengeyä"
        }
        
        # Handle derived pronouns
        if self.text.startswith(("fra", "'aw", "la", "fì", "tsa")) and self.text.endswith("po"):
            base = self.text[:-2]
            return base + "peyä"
        
        return irregular_genitives.get(self.text, self.text + "ä")
    
    def get_honorific_form(self) -> str:

        honorific_forms = {
            "oe": "ohe", "moe": "mohe", "pxoe": "pxohe", "ayoe": "ayohe",
            "oeng": "oheng", "pxoeng": "pxoheng", "ayoeng": "ayoheng",
            "nga": "ngenga", "menga": "mengenga", "pxenga": "pxengenga", "aynga": "ayngenga",
            "po": "poho"
        }
        
        if self.person == "third" and self.number == "singular" and self.animacy == "animate":
            return "pohan" if self.gender == "male" else "pohe"
        
        return honorific_forms.get(self.text, self.text)
    
    def get_gendered_form(self) -> str: # 3rd person 
        if (self.person == "third" and self.number == "singular" and self.animacy == "animate"):
            return "poan" if self.gender == "male" else "poe"
        return self.text
    
    def get_short_form(self) -> str:
        short_forms = {"ayoeng": "awnga", "ayfo": "fo", "aysa'u": "sa'u"}
        return short_forms.get(self.text, self.text)
    
    @property
    def is_animate(self) -> bool:
        return self.animacy == "animate"
    
    @property
    def is_inclusive(self) -> bool:
        return self.inclusivity == "inclusive"
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info.update({
            'person': self.person,
            'number': self.number,
            'animacy': self.animacy,
            'inclusivity': self.inclusivity,
            'gender': self.gender,
            'is_honorific': self.is_honorific
        })
        return info


class NaviVerb(InflectableWord):
    
    def __init__(
        self,
        text: str,
        position: int = 0,
        transitivity: str = "transitive",
        is_compound: bool = False,
    ):
        self.transitivity = transitivity
        self.is_compound = is_compound
        
        super().__init__(text, position)
    
    def get_word_type(self) -> str:
        return "verb"
    
    def apply_inflection(self, **kwargs) -> str:
        inflection_type = kwargs.get('type', 'infix')
        
        if inflection_type == 'infix':
            return self.add_infix(
                pre_first=kwargs.get('pre_first'),
                first=kwargs.get('first'),
                second=kwargs.get('second')
            )
        elif inflection_type == 'participle':
            return self.make_participle(kwargs.get('voice', 'active'))
        elif inflection_type == 'causative':
            return self.make_causative()
        elif inflection_type == 'reflexive':
            return self.make_reflexive()
        
        return self.text
    
    def add_infix(
        self,
        pre_first: Optional[str] = None,
        first: Optional[str] = None,
        second: Optional[str] = None,
    ) -> str:
        """Add infixes to verb"""
        result = self.text
        syllables = self._split_syllables(result)
        
        if pre_first and len(syllables) >= 2:
            result = self._insert_infix(result, pre_first, -2)
        
        if first:
            result = self._insert_infix(result, first, -2)
        
        if second:
            result = self._insert_infix(result, second, -1)
        
        self._infixed_form = result
        return result
    
    def _split_syllables(self, word: str) -> List[str]:
        vowels = "aeiìouä"
        syllables = []
        current = ""
        
        for char in word:
            current += char
            if char in vowels:
                syllables.append(current)
                current = ""
        
        if current:
            if syllables:
                syllables[-1] += current
            else:
                syllables.append(current)
        
        return syllables
    
    def _insert_infix(self, word: str, infix: str, syllable_index: int) -> str:
        syllables = self._split_syllables(word)
        
        if abs(syllable_index) > len(syllables):
            syllable_index = -1 if syllable_index < 0 else 0
        
        target_syllable = syllables[syllable_index]
        
        for i, char in enumerate(target_syllable):
            if char in "aeiìouä":
                new_syllable = target_syllable[:i] + infix + target_syllable[i:]
                syllables[syllable_index] = new_syllable
                break
        
        return "".join(syllables)
    
    def make_participle(self, voice: str = "active") -> str:
        infix = "us" if voice == "active" else "awn"
        return self.add_infix(first=infix)
    
    def make_causative(self) -> str:
        return self.add_infix(pre_first="eyk")
    
    def make_reflexive(self) -> str:
        return self.add_infix(pre_first="äp")
    
    @property
    def is_transitive(self) -> bool:
        return self.transitivity == "transitive"
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info.update({
            'transitivity': self.transitivity,
            'is_compound': self.is_compound,
            'is_transitive': self.is_transitive
        })
        return info


class NaviAdjective(InflectableWord):
    
    def __init__(
        self,
        text: str,
        position: int = 0,
        derived_with_le: bool = False,
        is_color: bool = False,
    ):
        self.derived_with_le = derived_with_le
        self.is_color = is_color
        
        super().__init__(text, position)
    
    def get_word_type(self) -> str:
        return "adjective"
    
    def apply_inflection(self, **kwargs) -> str:
        inflection_type = kwargs.get('type', 'attributive')
        
        if inflection_type == 'attributive':
            return self.make_attributive(kwargs.get('position', 'before'))
        elif inflection_type == 'adverb':
            return self.make_adverb()
        elif inflection_type == 'comparative':
            return self.make_comparative(
                kwargs.get('comparison', 'standard'),
                kwargs.get('compared_to')
            )
        elif inflection_type == 'color_noun':
            return self.make_color_noun()
        
        return self.text
    
    def make_attributive(self, position: str = "before") -> str:
        if self.derived_with_le and position == "after":
            return self.text
        else:
            if self.text.endswith("a"):
                return self.text
            return self.text + "a"
    
    def make_adverb(self) -> str:
        return "ni" + self.text
    
    def make_comparative(
        self, comparison: str = "standard", compared_to: Optional[str] = None
    ) -> str:
        if comparison == "standard":
            return f"to {compared_to}" if compared_to else "to"
        elif comparison == "superlative":
            return "frato"
        elif comparison == "equality":
            return f"niftxan {self.text} na {compared_to}"
        return self.text
    
    def make_color_noun(self) -> str:
        if self.is_color:
            if self.text.endswith("n"):
                return self.text[:-1] + "mpin"
            return self.text + "pin"
        return self.text
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info.update({
            'derived_with_le': self.derived_with_le,
            'is_color': self.is_color
        })
        return info


class NaviNumber(NaviWord): # octal system - 8 
    
    def __init__(self, text: str, position: int = 0, value: Optional[int] = None):
        self.value = value
        super().__init__(text, position)
    
    def get_word_type(self) -> str:
        return "number"
    
    def get_cardinal(self) -> str:
        numbers = {
            1: "'aw", 2: "mune", 3: "pxey", 4: "tsing",
            5: "mrr", 6: "pukap", 7: "kinä", 8: "vol"
        }
        return numbers.get(self.value, self.text) if self.value else self.text
    
    def get_ordinal(self) -> str:
        cardinal = self.get_cardinal()
        stem_changes = {
            "'aw": "'aw", "mune": "mu", "pxey": "pxey",
            "tsing": "tsi", "mrr": "mrr", "pukap": "pu",
            "kinä": "ki", "vol": "vol"
        }
        stem = stem_changes.get(cardinal, cardinal)
        return stem + "ve"
    
    def get_fraction(self) -> str:
        if self.value == 2:
            return "mawl"
        elif self.value == 3:
            return "pan"
        
        ordinal_stem = self.get_ordinal()[:-2]
        return ordinal_stem + "pxi"
    
    def get_adverbial(self) -> str:
        if self.value == 1:
            return "'awlo"
        elif self.value == 2:
            return "melo"
        elif self.value == 3:
            return "pxelo"
        else:
            return f"alo a{self.get_cardinal()}"
    
    def make_adverbial(self) -> str:
        return self.get_adverbial()
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info['value'] = self.value
        return info


class NaviParticle(NaviWord):
    
    def __init__(self, text: str, position: int = 0, particle_type: str = "general"):
        self.particle_type = particle_type
        super().__init__(text, position)
    
    def get_word_type(self) -> str:
        return "particle"
    
    def use_in_context(self, context: str) -> str:
        """Use particle in context"""
        if self.particle_type == "question":
            return f"{self.text} {context}"
        elif self.particle_type == "vocative":
            return f"ma {context}"
        elif self.particle_type == "negative":
            return f"{context} {self.text}"
        else:
            return f"{context} {self.text}"
    
    def is_question_particle(self) -> bool:
        return self.particle_type == "question"
    
    def is_vocative(self) -> bool:
        return self.particle_type == "vocative"
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info.update({
            'particle_type': self.particle_type,
            'is_question_particle': self.is_question_particle(),
            'is_vocative': self.is_vocative()
        })
        return info


class NaviPrenoun(NaviWord):
    
    def __init__(self, text: str, position: int = 0, prenoun_type: str = "deictic"):
        self.prenoun_type = prenoun_type
        super().__init__(text, position)
    
    def get_word_type(self) -> str:
        return "prenoun"
    
    def combine_with_noun(self, noun: str) -> str: # noun + vowel contraction
        # Special case for "fì" + "atan" -> "fìtan"
        if self.text == "fì" and noun == "atan":
            return "fìtan"
        
        if self.text.endswith("ì") and noun.startswith("a"):
            return self.text[:-1] + noun
        return self.text + noun
    
    def causes_lenition(self) -> bool:
        leniting_prenouns = ["pe"]
        return any(self.text.startswith(p) for p in leniting_prenouns)
    
    def get_grammatical_info(self) -> Dict[str, Union[str, int, bool]]:
        info = super().get_grammatical_info()
        info.update({
            'prenoun_type': self.prenoun_type,
            'causes_lenition': self.causes_lenition()
        })
        return info
