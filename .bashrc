# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# don't put duplicate lines in the history. See bash(1) for more options

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.

# make less more friendly for non-text input files, see lesspipe(1)


# export some env 

alias ls='ls --color=auto'
alias ll="ls -lhA --color"
alias pst="ps -eLf"
alias psa="ps auxww"
alias cs='cscope -bqk'
#alias ct='ctags -R --file-scope=yes --langmap=c:+.h --langmap=c++:+.inl --languages=c,c++ --links=yes --c-kinds=+p --c++-kinds=+p --fields=+iaS --extra=+q'
alias ct='ctags -R --c++-kinds=+px  --langmap=c++:+.inl --fields=+afmikKlnsStz --extra=+q $PWD' 
#alias gdb='cgdb'

#PS1='[\e[0;36m\u@\e[0;36m\h\e[0m \W]\$ '
#PS1='[\[\033[01;32m\]\h:\[\033[01;34m\]\W\[\033[00m\]]\$'

#PROMPT_COMMAND='printf "\033]0;%s@%s:%s\007" "${USER}" "${HOSTNAME%%.*}" "`basename ${PWD/#$HOME/~}`"'
PROMPT_COMMAND='printf "\033]0;%s@%s:%s\007" "${USER}" "${HOSTNAME%%.*}" "`basename ${PWD}`"'

# export LANG="C"
# export LC_ALL="C"
#export LANG="en_US.UTF-8"
export LANG="zh_CN.UTF-8"
export LC_ALL="zh_CN.UTF-8"
#export LANG="zh_CN.GBK"
#export LC_ALL="zh_CN.GBK"

export SVN_EDITOR="vim"
# User specific aliases and functions
export TERM=xterm-256color

