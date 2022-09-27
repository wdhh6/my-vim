# my-vim
this is my vim setting for c/c++

execute:
cp -r .bashrc .dir_colors .vim .vimrc ~/

then you can use the wdhh's vim

The setting is based on ctags, so please install the ctags(must be exuberant-ctags)

## First of all
when you enter a project, please execute 'ct' to generate the tags;

## keys
### to highlight the words(can highlight many words)
    highlight(enable or disable): shift + h 
    cancel the highlight of all words: shift + u
    
### go to function or members in struction definition 
    go to definiton:ctrl + ]
    go back: ctrl + t
    
 ### go to references
    go to the member in struction reference:gr
    got to the function reference: gw
    
    then you can use F5 to open the window to see what you want to see, and F6 to close the window, F7 to go to the next reference, F8 to go to preverious reference;
    
### taglist
    open the function list in a c or cpp file: F11
    
### open the current dir
    F3
    
### Code completion
    use tag completion:ctrl + x + o 
    use the keyword of the current file: ctrl + n
    

    
    
