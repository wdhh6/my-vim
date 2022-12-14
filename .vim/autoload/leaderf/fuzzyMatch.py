# Copyright (C) 2016 Yggdroot
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if sys.version_info >= (3, 0):
    def Unicode(str, encoding):
        return str
else:
    def Unicode(str, encoding):
        try:
            return unicode(str, encoding, 'ignore')
        except ValueError:
            return str


class FuzzyMatch(object):
    def __init__(self, pattern, encoding):
        self._pattern = Unicode(pattern, encoding)
        self._encoding = encoding
        self._pattern_mask = {}
        self._is_pattern_lower = (self._pattern + 'a').islower()
        for i, c in enumerate(self._pattern):
            if c in self._pattern_mask:
                self._pattern_mask[c] ^= (1 << i)
            else:
                self._pattern_mask[c] = ~0 ^ (1 << i)

    @staticmethod
    def evaluate(text, pattern, text_mask, j, pattern_mask, k, val):
        x = text_mask[pattern[0]] >> j
        # e.g., text = 'a~bc~d~~ab~~d~', pattern = 'abcd'
        if x == 0:
            return (0, 0, 0)
        # e.g., text = '~ab~~_abd~b~d', pattern = 'abbd'
        if k in val and val[k][2] > j + 1:
            return val[k]
        max_prefix_score = max_score = beg = end = 0
        i = ((x & -x) - 1).bit_length()
        if i == 0 or text[i-1] in '_- ':
            special = 2
        elif text[i].isupper():
            special = 2 if not text[i-1].isupper() else 0
        elif text[i-1] == '.':
            special = 1.9
        # elif text[i-1] in '/\\':
        #     special = 2
        elif not text[i-1].isalnum() :    # ;,"':...
            special = 2
        else:
            special = 0
        d = -2      # -0b10 or ~1
        i += 1
        text_len = len(text)
        pattern_len = len(pattern)
        while i < text_len:
            last = d
            c = text[i]
            if c in pattern_mask:
                d = d << 1 | pattern_mask[c] >> k
            elif (text[i-1].isupper() and c.lower() in pattern_mask and
                    (i+1 == text_len or not text[i+1].islower())):
                d = d << 1 | pattern_mask[c.lower()] >> k
            else:
                d = ~0
            if d >= last:
                n = (~last).bit_length()
                # e.g., text = '~~abcd~~~~', pattern = 'abcd'
                if n == pattern_len:
                    score = n*n + special
                    if special == 2:
                        val[k] = (score, i-n, j+i)
                        return val[k]
                    else:
                        end_pos = j + i
                else:
                    prefix_score = n*n + special
                    if prefix_score > max_prefix_score:
                        max_prefix_score = prefix_score
                        res = FuzzyMatch.evaluate(text[i:],
                                                  pattern[n:],
                                                  text_mask,
                                                  j+i,
                                                  pattern_mask,
                                                  k+n,
                                                  val)
                        score = prefix_score + res[0] if res[0] else 0
                        end_pos = res[2]
                    else:
                        score = 0
                if score > max_score:
                    max_score = score
                    beg = i - n
                    end = end_pos
            # e.g., text = 'a~c~~~~ab~c', pattern = 'abc',
            # to find the index of the second 'a'
            # `d == last` is for the case when text = 'kpi_oos1', pattern = 'kos'
            if d == ~0 or d == last:
                y = x >> i
                if y == 0:
                    break
                else:
                    i += ((y & -y) - 1).bit_length()
                    if text[i].isupper():
                        special = 2 if not text[i-1].isupper() else 0
                    elif text[i-1] in '_- ':
                        special = 2
                    elif text[i-1] == '.':
                        special = 1.9
                    elif text[i-1] in '/\\':
                        special = 2
                    # elif not text[i-1].isalnum() :    # ;,"'...
                    #     special = 2
                    else:
                        special = 0
                    d = -2      # -0b10 or ~1
                    i += 1
            else:
                i += 1
        else:
            # e.g., text = '~~~~abcd', pattern = 'abcd'
            if ~d >> (pattern_len - 1):
                score = pattern_len*pattern_len + special
                if score > max_score:
                    max_score = score
                    beg = i - pattern_len
                    end = j + i
        val[k] = (max_score, beg, end)
        return val[k]

    @staticmethod
    def evaluateOneChar(text, pattern):
        if pattern.isupper():
            beg = text.find(pattern)
            return 0 if beg == -1 else 1.0/(beg + 1) + 1.0/len(text)
        text_lower = text.lower()
        beg = text_lower.find(pattern)
        if beg == -1:
            return 0
        special = 0
        if text[beg].isupper() or beg == 0 or text[beg-1] in '_.- /\\':
            special = 2
        else:
            second = text_lower.find(pattern, beg + 1)
            if second != -1 and (text[second].isupper() or
                                 text[second-1] in '_.- /\\'):
                special = 2
                beg = second
        return special + 1.0/(beg + 1) + 1.0/len(text)

    @staticmethod
    def evaluateTwoChar(text, pattern, is_pattern_lower):
        if is_pattern_lower:
            text_lower = text.lower()
            beg = text_lower.find(pattern)
            special = 0
            if beg != -1:
                if text[beg].isupper() or beg == 0 or text[beg-1] in '_.- /\\':
                    special = 2
                else:
                    second_beg = text_lower.find(pattern, beg + 1)
                    if second_beg != -1 and (text[second_beg].isupper() or
                                             text[second_beg-1] in '_.- /\\'):
                        special = 2
                        beg = second_beg
                return 4 + special + (1 >> beg) + 1.0/(beg + 1) + 1.0/len(text)
            else:
                beg = text_lower.find(pattern[0])
                if beg == -1:
                    return 0
                if text[beg].isupper() or beg == 0 or text[beg-1] in '_.- /\\':
                    special = 2
                end = text_lower.find(pattern[1], beg + 1)
                if end == -1:
                    return 0
                if text[end].isupper() or end == 0 or text[end-1] in '_.- /\\':
                    special += 2
                else:
                    second_end = text_lower.find(pattern[1], end + 1)
                    if second_end != -1 and (text[second_end].isupper() or
                                             text[second_end-1] in '_.- /\\'):
                        if special != 2:
                            second_beg = text_lower.find(pattern[0], beg + 1, second_end)
                            if second_beg != -1 and (text[second_beg].isupper() or
                                                     text[second_beg-1] in '_.- /\\'):
                                special = 2
                                beg = second_beg
                        special += 2
                        end = second_end
                return 2 + special + (1 >> beg) + 1.0/(beg + end) + 1.0/len(text)
        elif pattern[0].isupper():
            beg = text.find(pattern[0])
            if beg == -1:
                return 0
            if pattern[1].isupper(): # e.g. pattern is 'AB'
                end = text.find(pattern[1], beg + 1)
                return 0 if end == -1 else 1.0/(beg + end) + 1.0/len(text)
            else:   # e.g. pattern is 'Ab'
                text_lower = text.lower()
                end = text_lower.find(pattern[1], beg + 1)
                if end == -1:
                    return 0
                elif end == beg + 1:
                    return 4 + (1 >> beg) + 1.0/(beg + end) + 1.0/len(text)
                special = 0
                if text[end].isupper() or text[end-1] in '_.- /\\':
                    special = 2
                else:
                    second_end = text_lower.find(pattern[1], end + 1)
                    if second_end != -1 and (text[second_end].isupper() or
                                             text[second_end-1] in '_.- /\\'):
                        special = 2
                return 2 + special + (1 >> beg) + 1.0/(beg + end) + 1.0/len(text)
        else: # e.g. pattern is 'aB'
            text_lower = text.lower()
            beg = text_lower.find(pattern[0])
            if beg == -1:
                return 0
            end = text.find(pattern[1], beg + 1)
            if end == -1:
                return 0
            special = 0
            if text[beg].isupper() or beg == 0 or text[beg-1] in '_.- /\\':
                special = 2
            else:
                second_beg = text_lower.find(pattern[0], beg + 1, end)
                if second_beg != -1 and (text[second_beg].isupper() or
                                         text[second_beg-1] in '_.- /\\'):
                    special = 2
                    beg = second_beg
            return 2 + special + (1 >> beg) + 1.0/(beg + end) + 1.0/len(text)

    def getWeight(self, text):
        text = Unicode(text, self._encoding)
        pattern_len = len(self._pattern)
        if pattern_len == 1:
            return FuzzyMatch.evaluateOneChar(text, self._pattern)
        elif pattern_len == 2:
            return FuzzyMatch.evaluateTwoChar(text, self._pattern,
                                              self._is_pattern_lower)
        j = 0
        first_char = self._pattern[0]
        last_char = self._pattern[-1]
        if self._is_pattern_lower:
            text_lower = text.lower()
            first_char_pos = text_lower.find(first_char)
            if first_char_pos == -1:
                return 0
            last_char_pos = text_lower.rfind(last_char, first_char_pos)
            if last_char_pos == -1:
                return 0
            text_mask = {}
            for c in self._pattern_mask:
                text_mask[c] = 0
            for i, c in enumerate(text_lower[first_char_pos : last_char_pos+1],
                                  first_char_pos):
                if c in text_mask:
                    text_mask[c] |= (1 << i)
                    if j < pattern_len and c == self._pattern[j]:
                        j += 1
        else:
            if first_char.isupper():
                first_char_pos = text.find(first_char)
            else:
                first_char_pos = -1
                for i, c in enumerate(text):
                    if first_char == c.lower():
                        first_char_pos = i
                        break
            if first_char_pos == -1:
                return 0
            if last_char.isupper():
                last_char_pos = text.rfind(last_char, first_char_pos)
            else:
                last_char_pos = -1
                for i, c in enumerate(reversed(text[first_char_pos:])):
                    if last_char == c.lower():
                        last_char_pos = len(text) - 1 - i
                        break
            if last_char_pos == -1:
                return 0
            text_mask = {}
            for c in self._pattern_mask:
                text_mask[c] = 0
            for i, c in enumerate(text[first_char_pos : last_char_pos+1],
                                  first_char_pos):
                if c.isupper():
                    if c in text_mask:
                        text_mask[c] |= (1 << i)
                    if c.lower() in text_mask:
                        text_mask[c.lower()] |= (1 << i)
                    if j < pattern_len and (c == self._pattern[j] or
                            c.lower() == self._pattern[j]):
                        j += 1
                else:
                    if c in text_mask:
                        text_mask[c] |= (1 << i)
                        if j < pattern_len and c == self._pattern[j]:
                            j += 1
        if j < pattern_len:
            return 0
        val = {}
        score, beg, end = FuzzyMatch.evaluate(text,
                                              self._pattern,
                                              text_mask,
                                              0,
                                              self._pattern_mask,
                                              0,
                                              val)
        return score + (1 >> beg) + 0.4/(end - beg) + 1.0/(beg + end) + 1.0/len(text)

    @staticmethod
    def evaluateHighlights(text, pattern, text_mask, j, pattern_mask, k, val):
        key = (j, k)
        if key in val:
            return val[key]
        x = text_mask[pattern[0]] >> j
        # e.g., text = 'a~bc~d~~ab~~d~', pattern = 'abcd'
        if x == 0:
            return (0, [])
        max_prefix_score = max_score = 0
        highlights = []
        i = ((x & -x) - 1).bit_length()
        if i == 0 or text[i-1] in '_- ':
            special = 2
        elif text[i].isupper():
            special = 2 if not text[i-1].isupper() else 0
        elif text[i-1] == '.':
            special = 1.9
        elif text[i-1] in '/\\':
            special = 2
        # elif not text[i-1].isalnum() :    # ;,"'...
        #     special = 2
        else:
            special = 0
        d = -2      # -0b10 or ~1
        i += 1
        text_len = len(text)
        pattern_len = len(pattern)
        while i < text_len:
            last = d
            c = text[i]
            if c in pattern_mask:
                d = d << 1 | pattern_mask[c] >> k
            elif (text[i-1].isupper() and c.lower() in pattern_mask and
                    (i+1 == text_len or not text[i+1].islower())):
                d = d << 1 | pattern_mask[c.lower()] >> k
            else:
                d = ~0
            if d >= last:
                n = (~last).bit_length()
                # e.g., text = '~~abcd~~~~', pattern = 'abcd'
                if n == pattern_len:
                    score = n*n + special
                    cur_highlights = [[i-n+j+1, n]]
                    if special == 2:
                        val[key] = (score, cur_highlights)
                        return val[key]
                else:
                    prefix_score = n*n + special
                    if prefix_score > max_prefix_score:
                        max_prefix_score = prefix_score
                        res = FuzzyMatch.evaluateHighlights(text[i:],
                                                            pattern[n:],
                                                            text_mask,
                                                            j+i,
                                                            pattern_mask,
                                                            k+n,
                                                            val)
                        score = prefix_score + res[0] if res[0] else 0
                        cur_highlights = [[i-n+j+1, n]] + res[1] if res[1] else []
                    else:
                        score = 0
                if score > max_score:
                    max_score = score
                    highlights = cur_highlights
            # e.g., text = 'a~c~~~~ab~c', pattern = 'abc',
            # to find the index of the second 'a'
            # `d == last` is for the case when text = 'kpi_oos1', pattern = 'kos'
            if d == ~0 or d == last:
                y = x >> i
                if y == 0:
                    break
                else:
                    i += ((y & -y) - 1).bit_length()
                    if text[i].isupper():
                        special = 2 if not text[i-1].isupper() else 0
                    elif text[i-1] in '_- ':
                        special = 2
                    elif text[i-1] == '.':
                        special = 1.9
                    elif text[i-1] in '/\\':
                        special = 2
                    # elif not text[i-1].isalnum() :    # ;,"'...
                    #     special = 2
                    else:
                        special = 0
                    d = -2      # -0b10 or ~1
                    i += 1
            else:
                i += 1
        else:
            # e.g., text = '~~~~abcd', pattern = 'abcd'
            if ~d >> (pattern_len - 1):
                score = pattern_len*pattern_len + special
                if score > max_score:
                    max_score = score
                    highlights = [[j+i-pattern_len+1, pattern_len]]
        val[key] = (max_score, highlights)
        return val[key]

    def getHighlights(self, text):
        """
        return a list of pair [col, length], where `col` is the column number(start
        from 1, the value must correspond to the byte index of `text`) and `length`
        is the length of the highlight in bytes.
        e.g., [ [2,3], [6,2], [10,4], ... ]
        """
        text = Unicode(text, self._encoding)
        first_char = self._pattern[0]
        last_char = self._pattern[-1]
        if self._is_pattern_lower:
            text_lower = text.lower()
            first_char_pos = text_lower.find(first_char)
            last_char_pos = text_lower.rfind(last_char, first_char_pos)
            text_mask = {}
            for c in self._pattern_mask:
                text_mask[c] = 0
            for i, c in enumerate(text_lower[first_char_pos : last_char_pos+1],
                                  first_char_pos):
                if c in text_mask:
                    text_mask[c] |= (1 << i)
        else:
            if first_char.isupper():
                first_char_pos = text.find(first_char)
            else:
                first_char_pos = -1
                for i, c in enumerate(text):
                    if first_char == c.lower():
                        first_char_pos = i
                        break
            if last_char.isupper():
                last_char_pos = text.rfind(last_char, first_char_pos)
            else:
                last_char_pos = -1
                for i, c in enumerate(reversed(text[first_char_pos:])):
                    if last_char == c.lower():
                        last_char_pos = len(text) - 1 - i
                        break
            text_mask = {}
            for c in self._pattern_mask:
                text_mask[c] = 0
            for i, c in enumerate(text[first_char_pos : last_char_pos+1],
                                  first_char_pos):
                if c.isupper():
                    if c in text_mask:
                        text_mask[c] |= (1 << i)
                    if c.lower() in text_mask:
                        text_mask[c.lower()] |= (1 << i)
                else:
                    if c in text_mask:
                        text_mask[c] |= (1 << i)
        val = {}
        score, highlights = FuzzyMatch.evaluateHighlights(text,
                                                          self._pattern,
                                                          text_mask,
                                                          0,
                                                          self._pattern_mask,
                                                          0,
                                                          val)
        for i, highlight in enumerate(highlights):
            col, length = highlight
            highlight[0] = len(text[:col-1].encode(self._encoding)) + 1
            highlight[1] = len(text[col-1:col-1+length].encode(self._encoding))

        return highlights

