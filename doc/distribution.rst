Replicated parallel transformation
==================================

Definitions
-----------

Let:

- N be numer of processors
- m be the number of processes to spawn
- t be the base
- n be the interval where n=2^i such that 2^(i-1) < m < 2^i
- id() be the id of the host processor
- f compression factor such that m > N, m/f < N < m/(f-1)

Example 1. (one dimensonal)
---------------------------

Transforming::

  par i:=1 for x do p(x)

To::

  proc d(val t, val n, val x) is
    if n = 0
    then p(t)
    else if x > n/2
    then 
    { d(t, n/2, n/2)
    | on ((procid()+t+n/2) rem NUM_CORES) / f do 
        d(t+n/2, n/2, x-n/2)
    }
    else d(t, n/2, x)

  d(0, nextpow2(x), x)

Example 2. (two dimensional)
----------------------------

Transforming::

  par i:=1 for x, j:=1 for y do p(x, y)

To::

  proc d(val t, val n, val m, ...) is
    if n = 0
    then p(t/((x*y)/x), t/((x*y)/y), ...)
    else if m > n/2
    then 
    { d(t, n/2, n/2, ...)
    | on ((procid()+t+n/2) rem N) / f do
        d(t+n/2, n/2, m-n/2, ...)
    }
    else d(t, n/2, m, ...)

  d(0, nextpow2(x*y), x*y, ...)

General case
------------

For dimensions of length d_1, d_2, ..., d_k and a process with identifier i the index
parameter for dimension d_i for 0 < i <= k is

    i/(N/d_i)

where

    N = d_1*d_2*...*d_k

