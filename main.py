from typing import Any, Optional, Sequence
import csv


class Ballot:
    """A single person's ranked choices.

    Attributes:
        timestamp: The timestamp of the vote.
        preference_stack: The order of their preferences. Each element is the 
            string representation of the candidate. preference_stack[0] is the
            most preferred.
    """
    def __init__(self, survey_response_line: Sequence[str], candidates: Sequence[str]):
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
        assert len(survey_response_line) == len(candidates)+1, 'This survey response doesn\'t have the correct number of rankings'
        self.timestamp = survey_response_line[0]
        survey_response = [int(i) for i in survey_response_line[1:]]

        self.preference_stack = [None] * len(candidates)
        assert set(survey_response) == set(range(1, len(candidates)+1)), 'Survey response should have exactly one candidate for each rank.'
        for candidate_num, rank_of_candidate in enumerate(survey_response):
            self.preference_stack[rank_of_candidate-1] = candidates[candidate_num]

    def __str__(self):
        return f'Ballot<{self.preference_stack}>'


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

        print(f'The candidates were: {self._candidates}')
        
        self._ballots = [Ballot(line, self._candidates) for line in votes_array[1:]]
        print('The parsed ballots:')
        for b in self._ballots:
            print(b)
        # Sort the ballots so that they get grouped by first choice and so on.
        self._ballots.sort(key=str) 
        print('After sorting:')
        for b in self._ballots:
            print(b)

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
            self._candidates[i] = candidate[len_question_asked+1:-1]

    def clear_winner(self) -> Optional[str]:
        pass

    def remove_least_popular(self) -> str:
        pass


def read_votes(file: str) -> Votes:
    with open(file, mode='r') as f:
        csv_file = csv.reader(f)
        lines = [line for line in csv_file]
    return Votes(lines)


def main():
    print('Starting the ranked choice vote count.')
    path = 'the_votes.csv'  # TODO: Take this as a command argument.
    votes = read_votes(path)

    while True:
        winner = votes.clear_winner()
        if winner is not None:
            print(f'Winner found!\nThe winner is {winner}')
            break
        removed = votes.remove_lease_popular()
        print(f'Removed {removed}')
        print(f'Remaining votes: {votes}')


if __name__ == '__main__':
    main()