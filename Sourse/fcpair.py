from functools import total_ordering

@total_ordering
class FrequencyCharPair:
    def __init__(self, frequency, character):
        self.frequency = frequency
        self.character = character

    def __lt__(self, other):
        if isinstance(other, FrequencyCharPair):
            return self.frequency < other.frequency
        return self.frequency < other

    def __eq__(self, other):
        if isinstance(other, FrequencyCharPair):
            return self.frequency == other.frequency
        return self.frequency == other
