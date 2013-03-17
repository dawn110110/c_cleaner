#!/usr/bin/env python
#encoding=utf-8

from parser import CodeSoup
import sys
import shutil
import os

def main():
    try:
        src = sys.argv[1]
    except:
        print 'you must specify an avaliable project path'
        return

    dst = src+'_clean'
    print 'src = %r' % src
    print 'dst = %r' % dst

    # copy files
    try:
        shutil.copytree(src, dst)
    except Exception, e:
        print e
        print 'Remove these files recursivly ? %r ' % dst
        ans = 'what'
        while ans.lower() not in ['yes', 'no']:
            ans = raw_input("type yes/no:")
        if ans == 'yes':
            shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            print 'give up works'
            return


    # walk through files, remove c comments ,and give statistics
    statistics = {}
    for root, dirs, files in os.walk(dst):
        for f in files:
            ff = 'xx'+f
            if ff[-2:] == '.c':
                with open(root+os.sep+f) as f_ob:
                    code_with_comment = f_ob.read()

                #  FIXME optimize line count later
                original_lines = len(code_with_comment.splitlines())  # bad
                soup = CodeSoup(code_with_comment)
                code_lines = len(soup.clean.splitlines())  # bad
                statistics[root+os.sep+f] = (original_lines,
                                             code_lines,
                                             soup.comments_line_count,
                                             soup.blank_line_count)
                with open(root+os.sep+f, 'w') as f_ob:
                    f_ob.write(soup.clean)

    # write statistics file
    with open(dst+os.sep+'comment_statistics.txt', 'w') as f:
        header =  "total\tcode\tcmts\tblank\tfilename\n"
        f.write(header)
        for k in statistics:
            f.write("%d\t%d\t%d\t%d\t%s\n" %
                    (statistics[k][0], statistics[k][1],
                     statistics[k][2], statistics[k][3], k))

    print 'finished!'
    print 'see:  ' + dst + os.sep + 'comment_statistics.txt'


if __name__ == "__main__":
    main()
