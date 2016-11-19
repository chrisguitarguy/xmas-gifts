#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import collections
import copy
import csv
import itertools
import random
import sys


def parse_args(args=None):
    p = argparse.ArgumentParser(description='Generate gift givers/receievers for the Reinke christmas gift exchange.')
    p.add_argument('-c', '--count', type=int, default=1,
        help='The number gifts each pearson should received')
    p.add_argument('filename', help='The input file. Should be a CSV with one family per line.')
    p.add_argument('-r', '--retries', type=int, default=5,
        help='The maximum number or retries the match maker should perform')

    return p.parse_args(args)


class CouldNotMatch(Exception):
    pass


class MatchMaker(object):

    def __init__(self, families, gift_count):
        self.families = families
        self.gift_count = gift_count
        self.counters = collections.defaultdict(int)

    def make_givers(self, family):
        givers = copy.deepcopy(self.families)
        del givers[family]
        givers = list(set(itertools.chain(*givers)) - set(filter(lambda x: self.counters[x] >= self.gift_count, self.counters)))
        random.shuffle(givers)

        return givers

    def match_person(self, family, person):
        give_to = self.make_givers(family)[:self.gift_count]
        # the filter for people that have gifts sometimes yields less than two
        # people. Has to do with odd numbers + the "randomness" of assinging gifts.
        if len(give_to) != self.gift_count:
            raise CouldNotMatch('Could not allocate {} people for {}'.format(self.gift_count, person))

        for person in give_to:
            self.counters[person] += 1

        return give_to

    def match(self):
        out = dict()
        for family, people in enumerate(self.families):
            for person in people:
                out[person] = self.match_person(family, person)

        return out

    def __call__(self, retries):
        for _ in range(retries):
            try:
                return self.match()
            except CouldNotMatch:
                continue

        return None


def read_input(filename):
    with open(filename) as fh:
        reader = csv.reader(fh)
        return list(reader)


def main(args=None):
    args = parse_args(args)

    families = read_input(args.filename);
    assert len(families) > 0, 'Cannot generate gifts for no families!'

    matcher = MatchMaker(families, args.count)
    matches = matcher(args.retries)

    if matches is None:
        print('Could not generate matches after {} retries.'.format(args.retries), file=sys.stderr)
        return 1

    for person, recipients in matches.items():
        print(person, '->', ', '.join(recipients))

    return 0

if __name__ == '__main__':
    sys.exit(main())
