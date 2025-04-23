from functools import total_ordering

@total_ordering
class HuffmanNode:
    def __init__(self, frequency, left=None, right=None, parent=None):
        self.frequency = frequency
        self.leftChild = left
        self.rightChild = right
        self.parent = parent

    def getChildren(self):
        """Returns both the left and right children of the node."""
        return self.leftChild, self.rightChild

    def __lt__(self, other):
        if isinstance(other, HuffmanNode):
            return self.frequency < other.frequency
        return self.frequency < other

    def __eq__(self, other):
        if isinstance(other, HuffmanNode):
            return self.frequency == other.frequency
        return self.frequency == other