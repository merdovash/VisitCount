from pathlib import Path

_file = Path(__file__)

done_img = str(_file.with_name('done.png'))
loading_gif = str(_file.with_name('loader.gif'))
qss = str(_file.with_name('style.qss'))
drop_arrow = str(_file.with_name('drop_arrow.gif'))

if __name__ == '__main__':
    print(done_img)
