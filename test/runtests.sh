#!/bin/bash

TEST_FILES='programs/*.sire'
COMPILE='../compiler/sire.py'

i=0
for file in $TEST_FILES
do
    name=${file%\.*}
    echo "Test $i: '$name'"

    # Compile the source file
    $COMPILE $file -o a.xe

    # Execute the binary on the simulator
    #xsim a.xe >> a.out

    # Compare the simulator output to the correct output
    #diff a.out ${name}.out

    # Clean up
    #rm a.xe a.out

    i=$(($i + 1))
done
