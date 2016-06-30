#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sortedcontainers import SortedSet

class Sentence:
    def __len__(self):
        return len(self.sentences)

    def __hash__(self):
        return hash(str(self))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return self.sentences.__iter__()

    def __getitem__(self, index):
        return self.sentences.__getitem__(index)

    def __len__(self):
        return len(self.sentences)

    def update(self, other):
        return self.sentences.update(other)

    def difference(self, other):
        return self.sentences.difference(other)

    def __lt__(self, other):
        return str(self) < str(other)

class Truth_Value(Sentence):
    def __init__(self, value):
        self.sentences = SortedSet([value])
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, Truth_Value):
            return False
        return self.value == other.value

class Symbol:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __lt__(self, other):
        return str(self) < str(other)

class Negation(Sentence):
    def __init__(self, sentence):
        self.sentences = SortedSet([sentence])
        self.sentence = sentence

    def __repr__(self):
        return "¬"+str(self.sentence)

    def __eq__(self, other):
        if isinstance(other, Negation):
            return self.sentence == other.sentence
        return False

class Conjunction(Sentence):
    def __init__(self, *sentences):
        self.sentences = SortedSet(sentences)

    def __repr__(self):
        return "("+" ∧ ".join([str(x) for x in self.sentences])+")"

    def __eq__(self, other):
        if isinstance(other, Conjunction):
            return self.sentences == other.sentences
        return False

class Disjunction(Sentence):
    def __init__(self, *sentences):
        self.sentences = SortedSet(sentences)

    def __repr__(self):
        return "("+" ∨ ".join([str(x) for x in self.sentences])+")"

    def __eq__(self, other):
        if isinstance(other, Disjunction):
            return self.sentences == other.sentences
        return False

class Implication(Sentence):
    def __init__(self, sentence1, sentence2):
        self.sentences = (sentence1, sentence2)

    def __repr__(self):
        return "(" + str(self.sentences[0]) + " ⇒ " + str(self.sentences[1]) + ")"

    def __eq__(self, other):
        if isinstance(other, Implication):
            return self.sentences == other.sentences
        return False

class Equivalence(Sentence):
    def __init__(self, sentence1, sentence2):
        self.sentences = (sentence1, sentence2)

    def __repr__(self):
        return "(" + str(self.sentences[0]) + " ⇔ " + str(self.sentences[1]) + ")"

    def __eq__(self, other):
        if isinstance(other, Implication):
            return self.sentences == other.sentences
        return False

def simplify_disjunction(sentence):
    # Associativity
    args = [simplify_sentence(s) for s in sentence.sentences]
    new_args = []
    while len(args) > 0:
        arg = args.pop()
        if isinstance(arg, Disjunction):
            args.extend(arg.sentences)
        else:
            new_args.append(arg)
    for s in new_args[:]:
        count = new_args.count(s)
        if count > 1:
            for x in range(count-1):
                new_args.remove(s)
        neg_s = simplify_sentence(Negation(s))
        count = new_args.count(neg_s)
        if count > 0:
            return Truth_Value(True)
    try:
        # Distributivity
        sentence = next((x for x in new_args if isinstance(x, Conjunction)))
        others = [x for x in new_args if not isinstance(x, Conjunction)]
        ss = list(sentence.sentences)
        if len(ss) == 2:
            return simplify_sentence(Conjunction(Disjunction(ss[0], *others),
                Disjunction(ss[1], *others)))
        return simplify_sentence(Conjunction(Disjunction(ss[0], *others),
                Disjunction(Conjunction(*ss[1:]), *others)))
    except StopIteration:
        return Disjunction(*new_args)

def simplify_sentence(sentence):
    # print ("Simplifying sentence: "+str(sentence))
    result = []
    if isinstance(sentence, Negation):
        ss = list(sentence.sentences)
        # De Morgan
        if isinstance(ss[0], Disjunction):
            negated_sentences = [Negation(s) for s in ss[0].sentences]
            return simplify_sentence(Conjunction(*negated_sentences))
        if isinstance(ss[0], Negation):
            return simplify_sentence(list(ss[0].sentences)[0])
    elif isinstance(sentence, Conjunction):
        if len(sentence.sentences) == 1:
            return simplify_sentence(list(sentence.sentences)[0])
        # Associativity
        args = [simplify_sentence(s) for s in sentence.sentences]
        new_args = []
        while len(args) > 0:
            arg = args.pop()
            if isinstance(arg, Conjunction):
                args.extend(arg.sentences)
            else:
                new_args.append(arg)
        return Conjunction(*new_args)
    elif isinstance(sentence, Disjunction):
        if len(sentence.sentences) == 1:
            return simplify_disjunction(list(sentence.sentences)[0])
        return simplify_disjunction(sentence)
    elif isinstance(sentence, Equivalence):
        # Eliminate Equivalence
        return simplify_sentence(Conjunction( \
            Implication(sentence.sentences[0], sentence.sentences[1]), \
            Implication(sentence.sentences[1], sentence.sentences[0])))
    elif isinstance(sentence, Implication):
        # Eliminate Implication
        return simplify_sentence(Disjunction( \
                Negation(sentence.sentences[0]), \
                sentence.sentences[1]))
    return sentence

class KnowledgeBase(Sentence):
    def __init__(self):
        self.kb = Conjunction()

    def add_sentence(self, sentence):
        self.kb.sentences.add(sentence)

    def simplify(self):
        self.kb = simplify_sentence(self.kb)

    def __repr__(self):
        return str(self.kb)

    def try_derive(self, sentence):
        kb = simplify_sentence(Conjunction(Negation(sentence), self.kb))

        if not self.is_knf(kb):
            print ("Error, could not reach KNF by simplification!")
            return False

        clauses = Conjunction()
        new_clauses = kb
        while True:
            print ("Derive loop")
            print ("old clauses", clauses)
            print ("new clauses", new_clauses)
            print ("KB total length", len(clauses)+len(new_clauses))

            really_new_clauses = Conjunction()
            print ("Combinations 1")
            for s1 in clauses:
                for s2 in new_clauses:
                    res = self.resolve(s1, s2)
                    if Truth_Value(False) in res:
                        return True
                    really_new_clauses.update(res)
            print ("Combinations 2")
            for i in range(0, len(new_clauses)):
                for j in range(i+1, len(new_clauses)):
                    res = self.resolve(new_clauses[i], new_clauses[j])
                    if Truth_Value(False) in res:
                        return True
                    really_new_clauses.update(res)
            print ("Done with Combinations")

            clauses.update(new_clauses)
            new_clauses = Conjunction()
            new_clauses.update(really_new_clauses.difference(clauses))
            if len(new_clauses) == 0:
                print ("No new clauses!")
                return False
            print ()
        print ("Unreachable code")
        return False

    def is_literal(self, sentence):
        if isinstance(sentence, Negation):
            if isinstance(sentence.sentence, Symbol):
                return True
            return False
        elif isinstance(sentence, Symbol):
            return True
        return False

    def is_knf(self, sentence):
        if not isinstance(sentence, Conjunction):
            return False
        for s in sentence.sentences:
            if isinstance(s, Disjunction):
                for s_ in s.sentences:
                    if not self.is_literal(s_):
                        return False
            elif self.is_literal(s):
                pass
            else:
                return False
        return True

    def resolve(self, sentence1, sentence2):
        #print ("Resolving", sentence1, sentence2)
        res = []
        if not isinstance(sentence1, Disjunction):
            sentence1 = Disjunction(sentence1)
        if not isinstance(sentence2, Disjunction):
            sentence2 = Disjunction(sentence2)
        for s in sentence1.sentences:
            neg_s = simplify_sentence(Negation(s))
            if neg_s in sentence2.sentences:
                first =  [s_ for s_ in sentence1.sentences if not s_ == s]
                second = [s_ for s_ in sentence2.sentences if not s_ == neg_s]
                first.extend(second)
                if len(first) == 0:
                    res.append(Truth_Value(False))
                elif len(first) == 1:
                    r = simplify_sentence(first[0])
                    if r != Truth_Value(True):
                        res.append(r)
                else:
                    r = simplify_sentence(Disjunction(*first))
                    if r != Truth_Value(True):
                        res.append(r)
        #print ("Result:", res)
        return res
