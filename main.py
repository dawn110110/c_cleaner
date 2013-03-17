#!/usr/bin/env python
#encoding=utf-8

from parser import CodeSoup
import sys
import shutil

def main():
    try:
        src = sys.argv[1]
    except:
        print '1st parameter is source directory,\
               you must speifily an avaliable project  path'
        return

    dst = src+'_clean'
    print 'src = %r' % src
    print 'dst = %r' % dst
if __name__ == "__main__":
    main()

#    s = CodeSoup(txt)
#    print 'comment line = %r' % s.comments_line_count
#    print 'blank line = %r' % s.blank_line_count
#    clean_txt = s.clean
#
#    f = open("./testfiles/abstract_clean.c", 'w')
#    f.write(clean_txt)
#    f.close()
