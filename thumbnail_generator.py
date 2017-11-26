import argparse
import ftplib
import getpass
import os
import time

from PIL import Image


class ImageResizer:

    f_to_resize = []

    def get_img_files(self, in_path):
        files = []
        os.chdir(in_path)
        for file in os.listdir(os.curdir):
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".jpeg") or file.endswith(".JPEG"):
                files.append([file])
        return files

    def resize_image(self, in_file, height):
        img = Image.open(in_file, mode='r')
        perc = float(float(height) / img.size[1])
        width = int(float(img.size[0]) * perc)
        img.thumbnail((width, height), Image.ANTIALIAS)
        half_w = int(img.size[0]/2.)
        half_h = int(img.size[1]/2.)
        cr = img.crop((half_w - 75,
                       half_h - 75,
                       half_w + 75,
                       half_h + 75))
        cr.save('%s%s.jpg' % (in_file.rsplit('.', 1)[0], 't'))
        # else:
            # img.save('%s%s.jpg' % (in_file.rsplit('.', 1)[0], 't'))

    def get_images(self):
        return self.f_to_resize

    def __init__(self, in_path):
        self.f_to_resize = self.get_img_files(in_path)
        for file in self.f_to_resize:
            self.resize_image(file[0], height)


class FTP:

    pics_dir = ''

    def connect_and_create_dir(self, storage_dir):
        self.ftp.set_debuglevel(2)

        _username = raw_input('Username: ')
        _passwd = getpass.getpass('Password: ')
        self.ftp.login(user=_username, passwd=_passwd)
        self.ftp.cwd(storage_dir)

        self.ftp.mkd(self.pics_dir)
        self.ftp.cwd(self.pics_dir)
        return self.ftp, self.pics_dir

    def save_to_ftp(self, in_files):
        for file in in_files:
            with open(file[0], 'r') as f:
                self.ftp.storbinary('STOR ' + file[0], f)

    def __init__(self, host, storage_dir, in_files):
        self.ftp = ftplib.FTP(host=host)
        self.pics_dir = '%s' % int(time.time())
        print self.pics_dir

        self.connect_and_create_dir(storage_dir)
        self.save_to_ftp(in_files)
        self.ftp.close()


class HTML:

    IMG_SRC = """<a href='/pics/%s/%s' taget=_blank><img src='/pics/%s/%s'></a>  """

    def generate(self, files, dir):
        with open('images.txt', 'w') as html:
            for f in files:
                html.write(self.IMG_SRC % (dir, f[0], dir, '%s%s.jpg' % (f[0].rsplit('.', 1)[0], 't')))
                if((files.index(f) + 1) % 4 == 0):
                    html.write('</br>')


    def __init__(self):
        pass

parser = argparse.ArgumentParser(description='Process some integers.')

if __name__ == '__main__':
    parser.add_argument('--files_path',
                        help='PATH to images to resize')
    parser.add_argument('--size', type=int,
                        help='thumbnail height, width [px]')
    parser.add_argument('--host',
                        help='ftp host')
    parser.add_argument('--storage_dir',
                        help='where to put files')

    args = parser.parse_args()
    in_path = args.files_path
    height = args.height
    host = args.host
    storage_dir = args.storage_dir

    resizer = ImageResizer(in_path)
    ftp = FTP(host, storage_dir, resizer.get_img_files(in_path))
    HTML().generate(resizer.get_images(), ftp.pics_dir)
