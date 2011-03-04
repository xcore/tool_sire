Vim sire syntax file
--------------------

To install vim syntax file for the sire language:

(instructions in vim > :help new-filetype)

mkdir ~/.vim
mkdir ~/.vim/syntax/
mkdir ~/.vim/ftdetect/

cp sire.vim ~/.vim/syntax/
vim ~/.vim/ftdetect/sire.vim

and add

au BufRead,BufNewFile *.sire set filetype=sire

