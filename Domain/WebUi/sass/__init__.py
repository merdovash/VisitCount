import os

import sass

if __name__ == '__main__':
    sass.compile(dirname=('sass', '../../../Server/css'), output_style='compressed')

