from typing import Any, Optional, Sequence

Votes = Any
Candidate = Any


def read_votes(file: str) -> Votes:
    pass


def find_winner(votes: Votes) -> Optional[Candidate]:
    pass


def remove_least_popular(votes: Votes) -> Candidate:
    pass


def main():
    print('Starting the ranked choice vote count.')
    path = 'the_votes.csv'  # TODO: Take this as a command argument.
    votes = read_votes(path)

    while True:
        winner = find_winner(votes)
        if winner is not None:
            print(f'Winner found!\nThe winner is {winner}')
            break
        removed = remove_least_popular(votes)
        print(f'Removed {removed}')
        print(f'Remaining votes: {votes}')


if __name__ == '__main__':
    main()