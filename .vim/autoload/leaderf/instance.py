#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from leaderf.utils import *


#*****************************************************
# LfInstance
#*****************************************************
class LfInstance(object):
    """
    This class is used to indicate the LeaderF instance, which including
    the tabpage, the window, the buffer, the statusline, etc.
    """
    def __init__(self, category,
                 before_enter_cb,
                 after_enter_cb,
                 before_exit_cb,
                 after_exit_cb):
        self._category = category
        self._before_enter = before_enter_cb
        self._after_enter = after_enter_cb
        self._before_exit = before_exit_cb
        self._after_exit = after_exit_cb
        self._tabpage_object = None
        self._window_object = None
        self._buffer_object = None
        self._buffer_name = lfEval("expand('$VIMRUNTIME/')") + category + '/LeaderF'
        self._win_height = float(lfEval("g:Lf_WindowHeight"))
        self._show_tabline = int(lfEval("&showtabline"))
        self._is_autocmd_set = False
        self._initStlVar()
        self._highlightStl()

    def _initStlVar(self):
        lfCmd("let g:Lf_{}_StlCategory = '-'".format(self._category))
        lfCmd("let g:Lf_{}_StlMode = '-'".format(self._category))
        lfCmd("let g:Lf_{}_StlCwd= '-'".format(self._category))
        lfCmd("let g:Lf_{}_StlTotal = '0'".format(self._category))

        stl = "%#Lf_hl_{0}_stlName# LeaderF "
        stl += "%#Lf_hl_{0}_stlSeparator0#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlCategory# %{{g:Lf_{0}_StlCategory}} "
        stl += "%#Lf_hl_{0}_stlSeparator1#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlMode# %(%{{g:Lf_{0}_StlMode}}%) "
        stl += "%#Lf_hl_{0}_stlSeparator2#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlCwd# %<%{{g:Lf_{0}_StlCwd}} "
        stl += "%#Lf_hl_{0}_stlSeparator3#%{{g:Lf_StlSeparator.left}}"
        stl += "%=%#Lf_hl_{0}_stlBlank#"
        stl += "%#Lf_hl_{0}_stlSeparator4#%{{g:Lf_StlSeparator.right}}"
        stl += "%#Lf_hl_{0}_stlLineInfo# %l/%L "
        stl += "%#Lf_hl_{0}_stlSeparator5#%{{g:Lf_StlSeparator.right}}"
        stl += "%#Lf_hl_{0}_stlTotal# Total: %{{g:Lf_{0}_StlTotal}} "
        self._stl = stl.format(self._category)

    def _highlightStl(self):
        lfCmd("call leaderf#colorscheme#highlight('{}')".format(self._category))

    def _setAttributes(self):
        lfCmd("setlocal nobuflisted")
        lfCmd("setlocal buftype=nofile")
        lfCmd("setlocal bufhidden=hide")
        lfCmd("setlocal noswapfile")
        lfCmd("setlocal nolist")
        lfCmd("setlocal number")
        lfCmd("setlocal norelativenumber")
        lfCmd("setlocal nospell")
        lfCmd("setlocal nowrap")
        lfCmd("setlocal nofoldenable")
        lfCmd("setlocal foldcolumn=0")
        lfCmd("setlocal shiftwidth=4")
        lfCmd("setlocal cursorline")
        lfCmd("setlocal filetype=leaderf")

    def _setStatusline(self):
        self.window.options["statusline"] = self._stl
        lfCmd("redrawstatus")
        if not self._is_autocmd_set:
            self._is_autocmd_set = True
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#setStatusline({}, '{}')"
                  .format(self.buffer.number, self._stl))
            lfCmd("autocmd WinEnter,FileType * call leaderf#colorscheme#setStatusline({}, '{}')"
                  .format(self.buffer.number, self._stl))

    def _createBufWindow(self, win_pos):
        self._win_pos = win_pos

        if win_pos != 'fullScreen':
            self._restore_sizes = lfEval("winrestcmd()")

        # clear the buffer first to avoid a flash
        if self._buffer_object:
            self.buffer.options['modifiable'] = True
            del self._buffer_object[:]

        if win_pos == 'bottom':
            lfCmd("silent! noa keepa keepj bo sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'top':
            lfCmd("silent! noa keepa keepj to sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'fullScreen':
            lfCmd("silent! noa keepa keepj $tabedit %s" % self._buffer_name)
        elif win_pos == 'left':
            lfCmd("silent! noa keepa keepj to vsp %s" % self._buffer_name)
        elif win_pos == 'right':
            lfCmd("silent! noa keepa keepj bo vsp %s" % self._buffer_name)
        else:
            lfCmd("echoe 'Wrong value of g:Lf_WindowPosition'")

        self._tabpage_object = vim.current.tabpage
        self._window_object = vim.current.window
        if self._buffer_object is None:
            self._buffer_object = vim.current.buffer
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlight('{}')"
                  .format(self._category))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)"
                  .format(self._category))

    def _enterOpeningBuffer(self):
        if (self._tabpage_object and self._tabpage_object.valid
            and self._window_object and self._window_object.valid):
            vim.current.tabpage = self._tabpage_object
            vim.current.window = self._window_object
            self._after_enter()
            return True
        return False

    def setStlCategory(self, category):
        lfCmd("let g:Lf_{}_StlCategory = '{}'".format(self._category, category) )

    def setStlMode(self, mode):
        lfCmd("let g:Lf_{}_StlMode = '{}'".format(self._category, mode))
        lfCmd("call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)"
              .format(self._category))

    def setStlCwd(self, cwd):
        lfCmd("let g:Lf_{}_StlCwd = '{}'".format(self._category, cwd))

    def setStlTotal(self, total):
        lfCmd("let g:Lf_{}_StlTotal = '{}'".format(self._category, total))

    def enterBuffer(self, win_pos):
        if self._enterOpeningBuffer():
            return

        self._before_enter()

        if win_pos == 'fullScreen':
            self._orig_tabpage = vim.current.tabpage
            if len(vim.tabpages) < 2:
                lfCmd("set showtabline=0")
            self._createBufWindow(win_pos)
        else:
            self._orig_win_nr = vim.current.window.number
            self._createBufWindow(win_pos)
        self._setAttributes()
        self._setStatusline()

        self._after_enter()

    def exitBuffer(self):
        self._before_exit()

        if self._win_pos == 'fullScreen':
            try:
                lfCmd("tabclose!")
                vim.current.tabpage = self._orig_tabpage
            except:
                lfCmd("new | only")

            lfCmd("set showtabline=%d" % self._show_tabline)
        else:
            if len(vim.windows) > 1:
                lfCmd("silent! hide")
                # 'silent!' is used to skip error E16.
                lfCmd("silent! exec '%d wincmd w'" % self._orig_win_nr)
                lfCmd(self._restore_sizes)
            else:
                lfCmd("bd")

        lfCmd("echo")

        self._after_exit()

    def setBuffer(self, content):
        self.buffer.options['modifiable'] = True
        self._buffer_object[:] = content

    @property
    def tabpage(self):
        return self._tabpage_object

    @property
    def window(self):
        return self._window_object

    @property
    def buffer(self):
        return self._buffer_object

    @property
    def currentLine(self):
        return vim.current.line if self._buffer_object is vim.current.buffer else None
