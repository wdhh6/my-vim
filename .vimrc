" Only do this part when compiled with support for autocommands.
if has("autocmd")

    " Enable file type detection.
    " Use the default filetype settings, so that mail gets 'tw' set to 72,
    " 'cindent' is on in C files, etc.
    " Also load indent files, to automatically do language-dependent indenting.
    filetype plugin indent on

    " Put these in an autocmd group, so that we can delete them easily.
    augroup vimrcEx
    au!

    " For all text files set 'textwidth' to 78 characters.
    autocmd FileType text setlocal textwidth=78

    " When editing a file, always jump to the last known cursor position.
    " Don't do it when the position is invalid or when inside an event handler
    " (happens when dropping a file on gvim).
    autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal g`\"" |
    \ endif

    augroup END

else
    set autoindent        " always set autoindenting on
endif " has("autocmd")

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" cscope setting
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"if has("cscope")
"    set csprg=/usr/local/bin/cscope
"    set csto=1
"    set cst 
"    set nocsverb
"    " add any database in current directory
"    if filereadable("cscope.out")
"        cs add ./cscope.out ./cscope.in.out ./cscope.po.out
"    elseif filereadable("../cscope.out")
"        cs add ../cscope.out ../cscope.in.out ../cscope.po.out
"    elseif filereadable("../../cscope.out")
"        cs add ../../cscope.out ../../cscope.in.out ../../cscope.po.out
"    elseif filereadable("../../../cscope.out")
"        cs add ../../../cscope.out ../../../cscope.in.out ../../../cscope.po.out
"    elseif filereadable("../../../../cscope.out")
"        cs add ../../../../cscope.out ../../../../cscope.in.out ../../../../cscope.po.out
"    endif
"    "set csverb
"endif

set t_Co=256

set ts=4
set nocompatible

" allow backspacing over everything in insert mode
set backspace=indent,eol,start

"if has("vms")
"  set nobackup     " do not keep a backup file, use versions instead
"else
"  set backup       " keep a backup file
"endif
set history=50      " keep 50 lines of command line history
set showcmd         " display incomplete commands
set incsearch       " do incremental searching

"map Q gq

inoremap <C-U> <C-G>u<C-U>

"In many terminal emulators the mouse works just fine, thus enable it.
"if has('mouse')
"  set mouse=a
"endif

" Switch syntax highlighting on, when the terminal has colors
" Also switch on highlighting the last used search pattern.
"if &t_Co > 2 || has("gui_running")

"colorscheme ron
colorscheme molokai
syntax on
set hlsearch
"endif
set expandtab tabstop=4 shiftwidth=4 "foldmethod=syntax
set shiftwidth=4
set autoindent      " always set autoindenting on
set number
set nofen
set noic " set ic to ignore case
"set tags=tags,./tags,../tags,../../tags,../../../tags,../../../../tags,../../../../../tags,../../../../../../tags
set tags=tags;,tags
set tags+=~/.vim/systags


"set foldmethod=indent
"set foldmethod=syntax

"set fileencodings=utf-8,gb2312,gbk,gb18030
"set fileencodings=gb2312,gbk,gb18030
"set fileencodings=gbk
set fileformats=unix
"set termencoding=utf-8
"set termencoding=gbk
"set encoding=prc
"set encoding=gbk
"set encoding=gb18030

set fileencodings=utf-8,ucs-bom,gb18030,gbk,gb2312,cp936
set termencoding=utf-8
set encoding=utf-8
set nocp
filetype plugin on
set tabstop=4
set softtabstop=4
set shiftwidth=4

""nmap <F8> :!make <CR>
nmap <F2> :vertical res+5 <CR>
nmap <F3> :vertical res-5 <CR>
let OmniCpp_MayCompleteScope = 1

set completeopt=menu,longest
"nmap w= :resize +10<CR>
"nmap w- :resize -10<CR>
"nmap w, :vertical resize -10<CR>
"nmap w. :vertical resize +10<CR>
inoremap <C-l> <Right>
nnoremap <space>co :copen<CR>
nnoremap <space>cc :cclose<CR>
nnoremap tn :tn<CR>
nnoremap tp :tp<CR>
nnoremap ma mA
nnoremap ms mS
nnoremap md mD
nnoremap 'a 'A
nnoremap 's 'S
nnoremap 'd 'D

set showcmd                     " display incomplete commands
set ruler                       " show the cursor position all the time
set wildignore=*.bak,*.o,*.e,*~ " wildmenu: ignore these extensions
set wildmenu                    " command-line completion in an enhanced mode

function! UpdateCtags()
    let curdir=getcwd()
    while !filereadable("./tags")
        cd ..
        if getcwd() == "/"
            break
        endif
    endwhile
    if filewritable("./tags")
        !ctags -R --file-scope=yes --langmap=c:+.h --langmap=c++:+.inl --languages=c,c++ --links=yes --c-kinds=+p --c++-kinds=+p --fields=+iaS --extra=+q &
    endif
    execute ":cd " . curdir
endfunction
"nmap <F10> :call UpdateCtags()<CR>
set scrolloff=8
set cursorline
"highlight CursorLine   cterm=NONE ctermbg=blue  ctermfg=NONE  guibg=NONE guifg=NONE
"highlight cFunction   cterm=NONE ctermbg=NONE  ctermfg=yellow  guibg=NONE guifg=NONE
"highlight Function   cterm=NONE ctermbg=NONE  ctermfg=yellow  guibg=NONE guifg=NONE
"highlight cOperator   cterm=NONE ctermbg=NONE  ctermfg=green  guibg=NONE guifg=NONE

map   <silent> <F3>        :Explore<CR>
nmap  <silent> <F4>        :exe ":ptag ".expand("<cword>")<CR>
map   <silent> <F5>        :copen<CR>
map   <silent> <F6>        :cclose<CR>
map   <silent> <F7>        :cp<CR>
map   <silent> <F8>        :cn<CR>

imap  <silent> <F3>   <Esc>:Explore<CR>
imap  <silent> <F4>   <Esc>:exe ":ptag ".expand("<cword>")<CR>
imap  <silent> <F5>   <Esc>:copen<CR>
imap  <silent> <F6>   <Esc>:cclose<CR>
imap  <silent> <F7>   <Esc>:cp<CR>
imap  <silent> <F8>   <Esc>:cn<CR>
inoremap <C-c> <ESC>
nnoremap <C-c> :q<CR>

inoremap  ,  ,<Space>
"-------------------------------------------------------------------------------
" autocomplete parenthesis, brackets and braces
"-------------------------------------------------------------------------------
"inoremap ( ()<Left>
"inoremap [ []<Left>
"inoremap { {}<Left>
"
vnoremap ( s()<Esc>P<Right>%
vnoremap [ s[]<Esc>P<Right>%
vnoremap { s{}<Esc>P<Right>%
"
"-------------------------------------------------------------------------------
" autocomplete quotes (visual and select mode)
"-------------------------------------------------------------------------------
xnoremap  '  s''<Esc>P<Right>
xnoremap  "  s""<Esc>P<Right>
xnoremap  `  s``<Esc>P<Right>
"
"-------------------------------------------------------------------------------
 noremap <silent> <F11>  <Esc><Esc>:Tlist<CR>
inoremap <silent> <F11>  <Esc><Esc>:Tlist<CR>

let Tlist_GainFocus_On_ToggleOpen = 1
let Tlist_Close_On_Select 				= 1

let tlist_make_settings  = 'make;m:makros;t:targets'
let tlist_qmake_settings = 'qmake;t:SystemVariables'

nnoremap gw :grep -r -w <cword> * --exclude=tags --exclude=*.o<CR>
nnoremap gr :grep -r -e '\-><cword>' -e '\.<cword>' * --exclude=tags --exclude=*.o<CR>
au BufWritePost *.c,*.cpp,*.h call UpdateCtags()
nnoremap zj zfi{
nnoremap zk zf%
vnoremap gw y:grep -r -E '<C-R>0' * --exclude=tags --exclude=*.o<CR>

let g:cpp_class_scope_highlight = 1
let g:cpp_member_variable_highlight = 1
let g:cpp_class_decl_highlight = 1
let g:cpp_posix_standard = 1
let g:cpp_experimental_simple_template_highlight = 1
let g:cpp_experimental_template_highlight = 1
let g:cpp_concepts_highlight = 1

nnoremap <leader>t :LeaderfTag<CR>
