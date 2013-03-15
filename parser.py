#!/usr/bin/env python
#encoding=utf-8

import os
import sys

EMPTY_SET = set([' ', '\t', '\n', '\v', '\f', '\r'])  # empty char set


class CodeSoup(object):

    #  status
    CODE = 1  # normal code
    BEGIN = 11  # text begin
    END = 12  # text end

    OTHER = -1  # don't know
    ERROR = -2  # error status

    COMMENT_C_1 = 20  # /
    COMMENT_C_2 = 21  # //
    COMMENT_C_3 = 22  # // asdasd  or  // balbalb \ \n
    COMMENT_C_4 = 23  # // asdasd \n

    COMMENT_CPP_1 = 21  # /  same as COMMENT_C_1
    COMMENT_CPP_2 = 32  # /*
    COMMENT_CPP_3 = 33  # /* blaba
    COMMENT_CPP_4 = 34  # /* blabla *
    COMMENT_CPP_5 = 35  # /* blabla */

    STR_SINGLE_1 = 41  # '
    STR_SINGLE_2 = 42  # 'x
    STR_SINGLE_3 = 43  # 'x'

    STR_DOUBLE_1 = 51  # "
    STR_DOUBLE_2 = 52  # " xx
    STR_DOUBLE_3 = 53  # "xxx"

    def __init__(self, raw, encoding='utf-8'):
        ''' default encoding, use utf-8'''
        self.raw = raw
        self.encoding = encoding

        self.clean_code = []  # no comments, will be joined with ''
        self.comments_line_count = 0

        self.length = len(self.raw)
        self.max_index = self.length - 1

        self.line_begin_index = 0
        self.cmt_begin_index = 0

        self.status = self.BEGIN

        self.method_map = {     #  status
            self.CODE: self.on_code,
            self.BEGIN: self.on_begin,
            self.END: self.on_end,

            #self.OTHER: self.on_other,
            self.ERROR: self.on_error,

            self.COMMENT_C_1: self.on_comment_c_1,
            self.COMMENT_C_2: self.on_comment_c_2,
            self.COMMENT_C_3: self.on_comment_c_3,
            self.COMMENT_C_4: self.on_comment_c_4,

            #self.COMMENT_CPP_1: self.on_comment_cpp_1,  # no need
            #self.COMMENT_CPP_2: self.on_comment_cpp_2,
            #self.COMMENT_CPP_3: self.on_comment_cpp_3,
            #self.COMMENT_CPP_4: self.on_comment_cpp_4,
            #self.COMMENT_CPP_5: self.on_comment_cpp_5,

            self.STR_SINGLE_1: self.on_str_single_1,
            self.STR_SINGLE_2: self.on_str_single_2,
            self.STR_SINGLE_3: self.on_str_single_3,

            #self.STR_DOUBLE_1: self.on_str_double_1,
            #self.STR_DOUBLE_2: self.on_str_double_2,
            #self.STR_DOUBLE_3: self.on_str_double_3,
            }

    def parse(self):
        self.index = 0
        self.line_no = 0
        print 'max_index = %r' % self.max_index
        while self.status != self.END:
            if self.index <= self.max_index:
                self.c = self.raw[self.index]

                print 'index = %r, self.c = %r, self.status = %r' % (
                        self.index, self.c, self.status)
                method = self.method_map[self.status]
                method()
            else:
                print 'index = %r, self.c = %r, self.status = %r' % (
                        self.index, self.c, self.status)
                method = self.method_map[self.status]
                method()
                self.status = self.END
                self.on_end()

        print 'begin joining'
        self.clean = ''.join(self.clean_code).rstrip()

    def on_begin(self):
        c = self.c
        if c == '/':
            self.status = self.COMMENT_C_1
        elif c == '\n':
            self.onLineEnd()  # callback
        else:
            self.status = self.CODE
        self.index += 1

    def on_error(self, hint='no hints'):
        print 'ERROR!, around:\n-----\n %s\n-----' %\
            self.raw[max(self.index-10, 0):min(self.index+10,self.max_index)]
        print 'hint: %s' % hint
        sys.exit(1)

    def on_code(self):
        c = self.c
        if c not in ['/', '"', "'"]:
            if c == '\n':
                line = self.raw[self.line_begin_index:self.index]
                print 'line = "%s"' % line
                self.clean_code.append(line)
                self.clean_code.append('\n')
                self.line_begin_index = self.index + 1
                self.onLineEnd()
        else:
            if c == '/':
                self.status = self.COMMENT_C_1
            elif c == "'":
                self.status = self.STR_SINGLE_1
            elif c == '"':
                self.status == self.STR_DOUBLE_1
        self.index += 1

    def on_comment_c_1(self):
        c = self.c
        if c == '/':
            self.status = self.COMMENT_C_2
        elif c == '*':
            self.status = self.COMMENT_CPP_2
        elif c == "'":
            self.status = self.STR_SINGLE_1
        elif c == '"':
            self.status == self.STR_DOUBLE_1
        else:
            self.status = self.CODE
        self.index += 1

    def on_comment_c_2(self):
        c = self.c
        if c == '\n':
            self.status = self.COMMENT_C_4
            self.onLineEnd()
        else:
            # really a comment 
            self.cmt_begin_index = self.index - 1  # record begin pos
            self.status = self.COMMENT_C_3
        self.index += 1

    def on_comment_c_3(self):
        c = self.c
        if c == '\\':  # \
            try:
                c_next = self.raw[self.index + 1]
            except IndexError:
                self.status = self.END
                return
            if c_next == '\n':
                self.index += 2
                self.status = self.COMMENT_C_3
                self.comments_line_count += 1  # multi line comments
                return
        elif c == '\n':
            print 'meet \\n, a comment ended'
            self.status = self.COMMENT_C_4
            self.onLineEnd()
        else:
            self.status = self.COMMENT_C_3
        self.index += 1

    def on_comment_c_4(self):
        print 'on comment c 4 , called'
        line = self.raw[self.line_begin_index:self.cmt_begin_index-1]
        line_set = set(line)
        diff = line_set - EMPTY_SET
        if diff:
            self.clean_code.append(line)
            self.clean_code.append('\n')
        else:
            # this is an empty line
            pass
        self.comments_line_count += 1  # line comment finished

        # remove blank lines
        c = self.c
        while c == '\n':
            self.index += 1
            if self.index >= self.max_index:
                self.status = self.END
                return
            c = self.raw[self.index]
        self.c = self.raw[self.index]

        # comment ended, treat next char as nornal code
        self.status = self.CODE
        self.line_begin_index = self.index
        self.onLineBegin()

    def on_str_single_1(self):
        c = self.c
        if c == '\\':
            self.index += 1

        # get close quote
        try:
            close_quote = self.raw[self.index+1]
        except IndexError:
            self.status = self.ERROR
            return

        # simple check
        if close_quote == "'":
            self.status = self.STR_SINGLE_3  # treat as nornal code
            self.status = self.CODE
            self.index += 1
        else:
            self.status = self.ERROR

    def on_str_single_2(self):
        pass

    def on_str_single_3(self):
        pass




    def on_end(self):
        pass

    def onLineEnd(self):
        pass

    def onLineBegin(self):
        pass



if __name__ == "__main__":
    txt = open("testfile.c").read()
    soup = CodeSoup(txt)
    soup.parse()
    print '*' * 20
    print soup.clean
    print '*' * 20
    print 'soup.clean = %r' % soup.clean
    print 'totally comment lines = %r' % soup.comments_line_count
    pass
