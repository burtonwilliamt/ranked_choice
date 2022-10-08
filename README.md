# Ranked Choice

Tools to process ranked choice data. I have previously used google surveys to
get ranked choice data from my friends. This code is intended to algorithmicly
perform an [Instant Runoff Vote](https://en.wikipedia.org/wiki/Instant-runoff_voting).

## Data Format

The tool expects the data to be provided as a labeled CSV, where the columns are
options and the rows are individuals ranked choices. This is an example `.csv`
file using the example on wikipedia:

```
Timestamp,Bob,Sue,Bill
a,1,3,2
b,2,1,3
c,3,2,1
d,1,3,2
e,2,1,3
```

Note that the first column *must* be titled `Timestamp`. This is a Google survey
convention, and assures the tool that the first column can be ignored. You can
use this first column for any identifier you chose, or leave it empty.

```
$ python main.py wikipedia_example.csv
Reading the votes from file...
Warning: failed to simplify the candidate names.
The candidates were: ['Bob', 'Sue', 'Bill']
The parsed ballots:
	Ballot<[' Bob', 'Bill', ' Sue']>
	Ballot<[' Sue', ' Bob', 'Bill']>
	Ballot<['Bill', ' Sue', ' Bob']>
	Ballot<[' Bob', 'Bill', ' Sue']>
	Ballot<[' Sue', ' Bob', 'Bill']>
After sorting:
	Ballot<[' Bob', 'Bill', ' Sue']>
	Ballot<[' Bob', 'Bill', ' Sue']>
	Ballot<[' Sue', ' Bob', 'Bill']>
	Ballot<[' Sue', ' Bob', 'Bill']>
	Ballot<['Bill', ' Sue', ' Bob']>
Count of choices at rank 2:
	Sue : 2
	Bill: 2
	Bob : 1
Last place is tied between {'Bill', 'Sue'}
Count of choices at rank 1:
	Bill: 2
	Sue : 1
Last place is 'Bill' with 2 votes in rank 1.
Removed 'Bill'
Remaining votes:
	Ballot<[' Bob', ' Sue']>
	Ballot<[' Bob', ' Sue']>
	Ballot<[' Sue', ' Bob']>
	Ballot<[' Sue', ' Bob']>
	Ballot<[' Sue', ' Bob']>
Candidate Sue has 3 votes which is more than a majority (2.5)
Winner found!
The winner is Sue
```