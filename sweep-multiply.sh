#! /bin/bash

txtund=$(tput sgr 0 1)          # Underline
txtbld=$(tput bold)             # Bold
txtred=$(tput setaf 1) #  red
txtblu=$(tput setaf 4) #  blue
txtwht=$(tput setaf 7) #  white
bldred=${txtbld}$(tput setaf 1) #  red
bldblu=${txtbld}$(tput setaf 4) #  blue
bldwht=${txtbld}$(tput setaf 7) #  white
txtrst=$(tput sgr0)             # Reset

#set -x

# For each memory type
for d in {2..32}; do
  #echo "$(($d*$d))"
  sed "s/val R is [0-9]\+/val R is $d/g" benchmark/matrixmul-grain.sire > tmp.sire
  echo -ne $txtred
  sire tmp.sire -n $(($d*$d))
  echo -ne $txtblu
  axe a.se -s --config tmp.cfg
  echo -ne $txtrst
done

