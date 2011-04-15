" Vim syntax file
" Language: sire

if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn case match

" Keywords
syn keyword	sType	     module var val port chanend chan
syn keyword	sKeyword     proc func return skip aliases connect
syn keyword	sKeyword     true false skip
syn keyword	sKeyword     on is

" Control structures
syn keyword	sStructure   if then else
syn keyword     sRepeat      while do for until to par

" Bracketing
syn match       sBrackets     /\[\|\]/
syn match       sParentheses  /(\|)/

" Operators
syn keyword  	sOperator    and or xor lor land
syn match       sOperator    /:=\|!\|?\|!!\|??\|::=/
syn match       sOperator    /<\|>\|+\|-\|\*\|\/\|\\\|=\|\~/
syn match       sOperator    /<<\|>>\|^\|&\||/

" Numbers
syn match       sNumber      "[0-9]+"
syn match       sNumber      "0[xX][0-9a-fA-F]+"
syn match       sNumber      "0[bB][0-1]*"

" Special characters
syn match       sSpecialChar  /\\'\|\\\|*#\(\[0-9A-F_\]\+\)/ contained

" Identifiers
syn match       sIdentifier  /\<[A-Z][A-Z0-9_]*\>/
syn match       sProcedure   /\<[A-Za-z.][A-Za-z0-9.]*\>/ contained

" String
syn region      sString      start=/"/ skip=/\M*"/ end=/"/ contains=xSpecialChar

" Character literal
syn region      sCharString  start=/'/ end=/'/ contains=xSpecialChar

" Comments
syn match       sComment     "%.*"

if version >= 508 || !exists("did_x_syntax_inits")
  if version < 508
    let did_x_syntax_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif
  
  HiLink sKeyword     Keyword
  HiLink sType        Type
  HiLink sStructure   Structure
  HiLink sRepeat      Repeat
  HiLink sIdentifier  Identifier
  HiLink sOperator    Operator
  HiLink sNumber      Number
  HiLink sBrackets    Type
  HiLink sParentheses Delimiter
  HiLink sString      String
  HiLink sCharString  String
  HiLink sComment     Comment

  delcommand HiLink
endif

let b:current_syntax = "sire"

" vim: ts=8
