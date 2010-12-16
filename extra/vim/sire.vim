" Vim syntax file
" Language:     x

if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn case match
syn keyword	xType	       module var port chanend int of const

syn keyword	xKeyword       proc func return skip aliases connect
"syn keyword xKeyword       chan core
syn keyword	xKeyword       true false
syn keyword	xKeyword       on
syn keyword	xKeyword       bit ext is rem with


syn keyword	xStructure     if then else
syn keyword xRepeat        while do to for when

syn match       xBrackets       /\[\|\]/
syn match       xParentheses    /(\|)/

syn keyword  	xOperator      and or xor
syn match       xOperator      /:=\|!\|?\|!!\|??\|::=/
syn match       xOperator      /<\|>\|+\|-\|\*\|\/\|\\\|=\|\~/
syn match       xOperator      /<<\|>>\|^\|&\||/

"syn match       xSpecialChar
"syn match       xChar

"syn match       xNumber        "0\+[1-7]\=[\t\n$,; ]"
"syn match       xNumber        "[1-9]\d*"
"syn match       xNumber        "0[0-7][0-7]\+"
syn match       xNumber        "0[xX][0-9a-fA-F]\+"
syn match       xNumber        "0[bB][0-1]*"

syn match       xSpecialChar	/\\'\|\\\|*#\(\[0-9A-F\]\+\)/ contained

syn match       xIdentifier    /\<[A-Z.][A-Z.0-9]*\>/
syn match       xFunction      /\<[A-Za-z.][A-Za-z0-9.]*\>/ contained

syn region      xString        start=/"/ skip=/\M*"/ end=/"/ contains=xSpecialChar
syn region      xCharString    start=/'/ end=/'/ contains=xSpecialChar

syn match       xComment       "%.*"
"syn region      xComment       start=/\/*/ end=/*\//

if version >= 508 || !exists("did_x_syntax_inits")
  if version < 508
    let did_x_syntax_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif
  
    HiLink xKeyword     Keyword
    HiLink xType        Type
    HiLink xStructure   Structure
    HiLink xRepeat      Repeat
    HiLink xIdentifier  Identifier
    HiLink xOperator    Operator
    HiLink xNumber      Number
    HiLink xBrackets    Type
    HiLink xParentheses Delimiter
    HiLink xString      String
    HiLink xCharString  String
    HiLink xComment     Comment

  delcommand HiLink
endif

let b:current_syntax = "x"

" vim: ts=8
