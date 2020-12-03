"""Base parser class."""


class BlockParser(object):
    """Parser built on rules that parse blocks of input."""

    def __init__(self, rules=[]):
        """Create a BlockParser, pre-loading a set of rules."""
        self.rules = []
        for rule in rules:
            self.add_rule(rule)

    def add_rule(self, rule):
        """Add a rule to this parser"""
        self.rules.append(rule)

    def parse(self, generator):
        """Parse an iterable source of strings into a generator."""
        gen = iter(generator)
        for line in gen:
            block = {}
            for rule in self.rules:
                if rule[0](line):
                    block = rule[1](line, gen)
                    break
            yield block
