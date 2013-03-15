#!/usr/bin/env python
#encoding=utf-8

from parser import CodeSoup
import sys

if __name__ == "__main__":
    argv = sys.argv
    txt = open("./testfiles/abstract.c").read()

    s = CodeSoup(txt)
    print 'comment line = %r' % s.comments_line_count
    print 'blank line = %r' % s.blank_line_count
    clean_txt = s.clean

    f = open("./clean.txt", 'w')
    f.write(clean_txt)
    f.close()
