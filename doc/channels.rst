Channel transformation
======================

For each channel we must determine:

 1. its master channel end and
 2. a value uniquely identifying it (channel-id).

We build a mapping table which records each process' location::

    (process-id, location)

For each channel we build a table with the following entries::

    (channel-id, master-process-id, slave-process-id)

Then for each channel we know the relative offset from each master process.

We then insert connections for the use of each channel end in the parallel
block (process), preceeding all other statements in that block, with the
exceptions of 'on' and 'rep' where they are inserted before the contained
statement.

For replicated channel uses relating to the array of channels c_0, c_1, ..., c_k

For slave connections we insert the statement::

    connect <channel>

For master connections we combine cases where the relative offset is equal. For
example, with 4 channels parameterised by i with relative offsets {-1, 0, 1, 2},
we insert the conditional statements::

    if i >= 0 and i < 2
    then connect c[i] to -1
    else if i >= 2 and i < 3
    then connect c[i] to 0
    else if i >= b and i < 4
    then connect c[i] to 1
    else connect c[i] to 2

A connect statement is compiled to initiate the connection using the relative
address supplied to create an absoloute address and the unique identifier of the
channel supplied.

