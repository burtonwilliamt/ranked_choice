from typing import Optional, Sequence
from collections import namedtuple
import csv
import sys

CANDIDATE_PADDING = 0


class Ballot:
    """A single person's ranked choices.

    Attributes:
        timestamp: The timestamp of the vote.
        preference_stack: The order of their preferences. Each element is the 
            string representation of the candidate. preference_stack[0] is the
            most preferred.
    """

    def __init__(self, survey_response_line: Sequence[str],
                 candidates: Sequence[str]):
        """Constructs a single Ballot object.

        Args:
            survey_response_line (Sequence[str]): The individual survey 
                response. This is a row taken out of the google sheet, for
                example:
                ['9/6/2022 21:30:21', '3', '2', '7', '6', '5', '1', '4']
            candidates (Sequence[str]): The ordered list of candidates. These
                were the titles of each column except for the "Timestamp"
                column. For example:
                [
                    'Miller Lite',
                    'Money $10 buy in',
                    'Ability to mute people in discord',
                    'Intro track when joining discord',
                    'Other discord feature',
                    'Chooses the cookie (see below)',
                    'Steam game (max $70)',
                ]
        """
        assert len(survey_response_line) == len(
            candidates
        ) + 1, 'This survey response doesn\'t have the correct number of rankings'
        self.timestamp = survey_response_line[0]
        survey_response = [int(i) for i in survey_response_line[1:]]

        self.preference_stack = [None] * len(candidates)
        assert set(survey_response) == set(
            range(1,
                  len(candidates) + 1)
        ), 'Survey response should have exactly one candidate for each rank.'
        for candidate_num, rank_of_candidate in enumerate(survey_response):
            self.preference_stack[rank_of_candidate -
                                  1] = candidates[candidate_num]

    def __str__(self):
        candidates = ', '.join([
            f'\'{c.rjust(CANDIDATE_PADDING)}\'' for c in self.preference_stack
        ])
        return f'Ballot<[{candidates}]>'

    def remove_candidate(self, candidate: str):
        self.preference_stack.remove(candidate)


CandidateCountAtRank = namedtuple('CandidateCountAtRank',
                                  ['candidate', 'count'])


class Votes:
    """A mutable class to store ranked choice votes."""

    def __init__(self, votes_array: list[list[str]]):
        """Constructs a Votes instance.
        
        Args:
           votes_array: A list where each element is a row from the original
           table. The first row should be column titles. The first column should
           be timestamps.
        """
        assert votes_array[0][
            0] == 'Timestamp', 'Votes should have a timestamp.'

        self._candidates = votes_array[0][1:]
        self._simplify_candidate_names()
        global CANDIDATE_PADDING
        CANDIDATE_PADDING = max([len(c) for c in self._candidates])

        print(f'The candidates were: {self._candidates}')

        self._ballots = [
            Ballot(line, self._candidates) for line in votes_array[1:]
        ]
        print('The parsed ballots:')
        print(self)
        self._sort_ballots()
        print('After sorting:')
        print(self)

    def __str__(self):
        return '\n'.join(['\t' + str(b) for b in self._ballots])

    def _simplify_candidate_names(self):
        # Google survey includes the original question as a prefix on each
        # title. This removes that prefix.
        if any([c.count('[') != 1 for c in self._candidates]):
            # We can't just split on the '[', so abort. You could probably do
            # this better by finding the longes matching prefix shared by all
            # candidates but I don't care that much right now. I think splitting
            # on '[' should be good enough for now.
            print('Warning: failed to simplify the candidate names.')
            return
        len_question_asked = len(self._candidates[0].split('[')[0])
        for i, candidate in enumerate(self._candidates):
            self._candidates[i] = candidate[len_question_asked + 1:-1]

    def _sort_ballots(self):
        """Sorts the ballots so that they get grouped by first choice and so on."""
        self._ballots.sort(key=str)

    def _candidate_counts_at_rank(self, rank: int) -> list[tuple[str, int]]:
        """Counts how many times each candidate appeared at specified rank."""
        counts_at_rank = {}
        for ballot in self._ballots:
            choice = ballot.preference_stack[rank]
            counts_at_rank[choice] = counts_at_rank.get(choice, 0) + 1
        res = [
            CandidateCountAtRank(candidate=choice, count=count)
            for choice, count in counts_at_rank.items()
        ]
        res.sort(key=lambda x: x.count, reverse=True)
        return res

    def clear_winner(self) -> Optional[str]:
        first_choice_counts = self._candidate_counts_at_rank(0)
        if first_choice_counts[0].count > len(self._ballots) / 2:
            print(
                f'Candidate {first_choice_counts[0].candidate} has {first_choice_counts[0].count} votes which is more than a majority ({len(self._ballots)/2})'
            )
            return first_choice_counts[0].candidate
        return None

    def _remove_candidate(self, candidate: str):
        for ballot in self._ballots:
            ballot.remove_candidate(candidate)
        self._candidates.remove(candidate)
        self._sort_ballots()

    def remove_least_popular(self) -> str:
        """Removes the least popular candidate from all ballots.
        
        If one candidate has a majority of the last rank, it is removed. If
        there is a tie it is broken by proceeding up the ranks until one
        candidate has more votes. That candidate will be removed.

        For example:
        1st      4th
        A, B, C, D
        A, B, C, D
        B, A, D, C
        D, B, A, C
        
        D and C are tied for 4th rank. To find which one should "lose" we
        proceed up to the next rank (3rd) and check again. Only considering D
        and C, in the third rank C has more votes so we should remove C.

        Intuitively, this happens when an equal number of people place C and D
        in last rank, but the people who didn't place D in last place favor it
        much more than the people who didn't place C in last place favor C.
        """
        current_rank = len(self._candidates) - 1

        potential_losers = set(self._candidates)
        while current_rank >= 0:
            current_rank_counts = list(filter(
                lambda x: x.candidate in potential_losers,
                self._candidate_counts_at_rank(current_rank)))

            print(f'Count of choices at rank {current_rank}:')
            for choice, count in current_rank_counts:
                print(f'\t{choice.ljust(CANDIDATE_PADDING)}: {count}')

            if current_rank_counts[0].count > current_rank_counts[1].count:
                loser = current_rank_counts[0].candidate
                print(
                    f'Last place is \'{loser}\' with {current_rank_counts[0].count} votes in rank {current_rank}.'
                )
                self._remove_candidate(loser)
                return loser

            plurality_count = current_rank_counts[0].count
            potential_losers = {
                choice for choice, count in current_rank_counts
                if count == plurality_count
            }
            print(f'Last place is tied between {potential_losers}')
            current_rank -= 1
        raise ValueError('The remaining choices are tied, cannot select a winner.')


def read_votes(file: str) -> Votes:
    with open(file, mode='r') as f:
        csv_file = csv.reader(f)
        lines = [line for line in csv_file]
    return Votes(lines)


def main():
    if len(sys.argv) != 2:
        print(f'Usage: $python {sys.argv[0]} rel/path/to/votes.csv')
        return
    path = sys.argv[1]

    print('Reading the votes from file...')
    votes = read_votes(path)

    while True:
        winner = votes.clear_winner()
        if winner is not None:
            print(f'Winner found!\nThe winner is {winner}')
            break
        removed = votes.remove_least_popular()
        print(f'Removed \'{removed}\'')
        print(f'Remaining votes:\n{votes}')


if __name__ == '__main__':
    main()