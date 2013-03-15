#!/usr/bin/env python
#encoding=utf-8
'''
TODOs:
    1 . compatible on windows and linux
    2 . command line args
    3 . encoding transform
    4 . others
    '''
import sys

__all__ = ['CodeSoup', 'EMPTY_SET']

EMPTY_SET = set([' ', '\t', '\n', '\v', '\f', '\r'])  # empty char set


class CodeSoup(object):
    '''
    Only support C code. remove comments and blank lines
    usuage:
        >>> txt = open('xxx.c')
        >>> soup = CodeSoup(txt)
        >>> soup.blank_line_count
        >>> soup.comments_line_count
        >>> soup.clean
    '''

    #  status
    CODE = 1  # normal code
    BEGIN = 11  # text begin
    END = 12  # text end

    OTHER = -1  # don't know
    ERROR = -2  # error status

    # SLASH
    COMMENT_SLASH_1 = 20  # /
    COMMENT_SLASH_2 = 21  # //
    COMMENT_SLASH_3 = 22  # // asdasd  or  // balbalb \ \n
    COMMENT_SLASH_4 = 23  # // asdasd \n

    # STAR
    COMMENT_STAR_1 = 21  # /  same as COMMENT_SLASH_1
    COMMENT_STAR_2 = 32  # /*
    COMMENT_STAR_3 = 33  # /* blaba
    COMMENT_STAR_4 = 34  # /* blabla *
    COMMENT_STAR_5 = 35  # /* blabla */

    # single quote
    STR_SINGLE_1 = 41  # '
    STR_SINGLE_2 = 42  # 'x
    STR_SINGLE_3 = 43  # 'x'

    # double qoute
    STR_DOUBLE_1 = 51  # "
    STR_DOUBLE_2 = 52  # " xx
    STR_DOUBLE_3 = 53  # "xxx"

    def __init__(self, raw, encoding='utf-8'):
        ''' default encoding, use utf-8'''
        self.raw = raw
        self.encoding = encoding

        self.clean_code = []  # no comments, will be joined with ''
        self.comments_line_count = 0
        self.blank_line_count = 0
        self.after_star_comment = False  # a star comment ended, this set True

        self.length = len(self.raw)
        self.max_index = self.length - 1

        self.line_begin_index = 0
        self.cmt_begin_index = 0

        self.status = self.BEGIN

        self.method_map = {     # status
            self.CODE: self.on_code,
            self.BEGIN: self.on_begin,
            self.END: self.on_end,

            #self.OTHER: self.on_other,
            self.ERROR: self.on_error,

            self.COMMENT_SLASH_1: self.on_comment_slash_1,
            self.COMMENT_SLASH_2: self.on_comment_slash_2,
            self.COMMENT_SLASH_3: self.on_comment_slash_3,
            self.COMMENT_SLASH_4: self.on_comment_slash_4,

            self.COMMENT_STAR_1: self.on_comment_star_1,  # no need
            self.COMMENT_STAR_2: self.on_comment_star_2,
            self.COMMENT_STAR_3: self.on_comment_star_3,
            self.COMMENT_STAR_4: self.on_comment_star_4,
            self.COMMENT_STAR_5: self.on_comment_star_5,

            self.STR_SINGLE_1: self.on_str_single_1,
            self.STR_SINGLE_2: self.on_str_single_2,
            self.STR_SINGLE_3: self.on_str_single_3,

            self.STR_DOUBLE_1: self.on_str_double_1,
            self.STR_DOUBLE_2: self.on_str_double_2,
            self.STR_DOUBLE_3: self.on_str_double_3,
        }
        self.parse()

    def parse(self):
        self.index = 0
        self.line_no = 0
        # print 'max_index = %r' % self.max_index
        while self.status != self.END:
            if self.index <= self.max_index:
                self.c = self.raw[self.index]

                # print 'index = %r, self.c = %r, self.status = %r' % (
                #    self.index, self.c, self.status)
                method = self.method_map[self.status]
                method()
            else:
                #print 'index = %r, self.c = %r, self.status = %r' % (
                #    self.index, self.c, self.status)
                method = self.method_map[self.status]
                method()
                self.status = self.END
                self.on_end()

        #print 'begin joining'
        self.clean = ''.join(self.clean_code).rstrip()

    def on_begin(self):
        c = self.c
        if c == '/':
            self.status = self.COMMENT_SLASH_1
        elif c == '\n':
            self.onLineEnd()  # callback
        else:
            self.status = self.CODE
        self.index += 1

    def on_error(self, pos=None, hint='no hints'):
        pos = pos or self.index
        #print 'ERROR!, around:\n-----\n ...%s...\n-----' %\
        #    self.raw[max(pos-10, 0):min(pos+10, self.max_index)]
        #print 'hint: %s' % hint
        sys.exit(1)

    def on_code(self):
        #print ' - on_code, called',
        c = self.c
        if c in ['\n']:
            line = self.raw[self.line_begin_index:self.index]
            line_set = set(line)
            diff = line_set - EMPTY_SET
            if diff:
                #print 'line = "%s"' % line
                self.clean_code.append(line)
                self.clean_code.append('\n')
                self.index += 1

                self.line_begin_index = self.index  # for // cmt
                self.code_line_begin_index = self.index  # for /* cmt

                self.onLineEnd()
            else:
                if self.after_star_comment:
                    self.after_star_comment = False
                else:
                    self.blank_line_count += 1
                #print 'EMPTY'
                self.index += 1
                self.line_begin_index = self.index
        else:
            if c == '/':
                self.status = self.COMMENT_SLASH_1
            elif c == "'":
                self.status = self.STR_SINGLE_1
            elif c == '"':
                self.status = self.STR_DOUBLE_1
                self.d_qoute_begin_pos = self.index
            else:
                pass
            self.index += 1

    def on_comment_slash_1(self):
        c = self.c
        if c == '/':
            self.status = self.COMMENT_SLASH_2
        elif c == '*':
            self.status = self.COMMENT_STAR_2
        elif c == "'":
            self.status = self.STR_SINGLE_1
        elif c == '"':
            self.status == self.STR_DOUBLE_1
        else:
            self.status = self.CODE
        self.index += 1

    def on_comment_slash_2(self):
        c = self.c
        if c == '\n':
            self.status = self.COMMENT_SLASH_4
            self.onLineEnd()
        else:
            # really a comment
            self.cmt_begin_index = self.index - 1  # record begin pos
            self.status = self.COMMENT_SLASH_3
        self.index += 1

    def on_comment_slash_3(self):
        c = self.c
        if c == '\\':  # \
            try:
                c_next = self.raw[self.index + 1]
            except IndexError:
                self.status = self.END
                return
            if c_next == '\n':
                self.index += 2
                self.status = self.COMMENT_SLASH_3
                self.comments_line_count += 1  # multi line comments
                return
        elif c == '\n':
            self.status = self.COMMENT_SLASH_4
            self.onLineEnd()
        else:
            self.status = self.COMMENT_SLASH_3
        self.index += 1

    def on_comment_slash_4(self):
        line = self.raw[self.line_begin_index:self.cmt_begin_index-1]
        line_set = set(line)
        diff = line_set - EMPTY_SET
        if diff:
            self.clean_code.append(line)
            self.clean_code.append('\n')
        else:
            pass
            #print 'EMPTY'

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
            #  print 'close_quote = %r' % close_quote
        except IndexError:
            self.status = self.ERROR
            self.on_error(""" ' has to be closed, but file ended""")

        # simple check
        if close_quote == "'":
            self.status = self.STR_SINGLE_3  # treat as nornal code
            self.status = self.CODE
            self.index += 2
        else:
            self.status = self.ERROR
            self.on_error(hint=""" ' has to be closed with ' """)

    def on_str_single_2(self):
        ''' this will never be called'''
        pass

    def on_str_single_3(self):
        ''' this will never be called'''
        pass

    def on_str_double_1(self):
        ''' same as double_1 '''
        self.on_str_double_2()

    def on_str_double_2(self):
        c = self.c
        if c == '"':  # "
            #print 'index = %r, double quote end' % self.index
            self.status = self.CODE
            self.index += 1
        elif c == "\\":  # \
            self.status = self.STR_DOUBLE_2
            self.index += 2
        elif self.index == self.max_index:
            self.on_error(pos=self.d_qoute_begin_pos,
                          hint=''' " has to be closed''')
        else:
            self.status = self.STR_DOUBLE_2
            self.index += 1
        pass

    def on_str_double_3(self):
        ''' status same as CODE. this method will never be called'''
        pass

    def on_comment_star_1(self):
        ''' same as slash comment 1 '''
        self.on_comment_slash_2()

    def on_comment_star_2(self):
        c = self.c
        if c == '\n':
            self.comments_line_count += 1  # another line comment begin
            self.index += 1
        elif c == '*':
            self.status = self.COMMENT_STAR_4
            self.index += 1
        else:
            self.status = self.COMMENT_STAR_3  # nornal char
            self.index += 1

    def on_comment_star_3(self):
        ''' normal char '''
        self.on_comment_star_2()

    def on_comment_star_4(self):
        c = self.c
        if c == '/':
            self.status = self.COMMENT_STAR_5  # really end
            self.index += 1
        elif c == '\n':
            self.comments_line_count += 1
            self.index += 1
        else:
            self.status = self.COMMENT_STAR_3  # back to normal
            self.index += 1

    def on_comment_star_5(self):
        self.after_star_comment = True
        self.line_begin_index = self.index
        self.comments_line_count += 1
        self.c = self.raw[self.index]
        self.status = self.CODE

    def on_end(self):
        pass

    def onLineEnd(self):
        pass

    def onLineBegin(self):
        pass


if __name__ == "__main__":
    txt = open("./testfiles/simple.c").read()
    soup = CodeSoup(txt)
    print txt,
    print '*' * 20
    print soup.clean
    print '*' * 20
    print 'soup.clean = %r' % soup.clean
    print 'totally comment lines = %r' % soup.comments_line_count
    print 'total black lindes = %r' % soup.blank_line_count
    pass
