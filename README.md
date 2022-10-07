# Ranked Choice

Tools to process ranked choice data. I have previously used google surveys to
get ranked choice data from my friends. This code is intended to algorithmicly
perform an [Instant Runoff Vote](https://en.wikipedia.org/wiki/Instant-runoff_voting).

## Data Format

The tool expects the data to be provided as a labeled CSV, where the columns are
options and the rows are individuals ranked choices.