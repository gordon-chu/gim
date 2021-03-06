# Code mostly from https://pythonhosted.org/pyftpdlib/tutorial.html 
import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# TODO: make a config file for this
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VIDEO_STORE = os.path.join(BASE_DIR, 'videos')
HOF_STORE = os.path.join(BASE_DIR, 'videos/hof')
BV_STORE = os.path.join(BASE_DIR, 'videos/banned')
THUMBNAIL_STORE = os.path.join(BASE_DIR, 'videos/thumbnails')


class VideoServer:
    def __init__(self, host, port):
        authorizer = DummyAuthorizer()
        # TODO: properly store credentials in a config file

        # read-only user for searching videos
        authorizer.add_user('searcher', 'password', VIDEO_STORE, perm='r') 
        # delete-only user for removing videos (script)
        authorizer.add_user('deleter', 'password', VIDEO_STORE, perm='d')
        # write-only user for posting videos
        authorizer.add_user('poster', 'password', VIDEO_STORE, perm='w')

        # read-only user for searching hof videos
        authorizer.add_user('hof_searcher', 'password', HOF_STORE, perm='r') 
        # delete-only user for removing hof videos (script)
        authorizer.add_user('hof_deleter', 'password', HOF_STORE, perm='d')
        # write-only user for posting hof videos
        authorizer.add_user('hof_poster', 'password', HOF_STORE, perm='w')

        # read-only user for searching banned videos
        authorizer.add_user('banned_videos_searcher', 'password', BV_STORE, perm='r') 
        # write-only user for posting banned videos
        authorizer.add_user('banned_videos_poster', 'password', BV_STORE, perm='w')

        # read-only user for searching thumbnails
        authorizer.add_user('thumb_searcher', 'password', THUMBNAIL_STORE, perm='r') 
        # delete-only user for removing thumbnails
        authorizer.add_user('thumb_deleter', 'password', THUMBNAIL_STORE, perm='d')
        # write-only user for posting thumbnails
        authorizer.add_user('thumb_poster', 'password', THUMBNAIL_STORE, perm='w')

        handler = FTPHandler
        handler.authorizer = authorizer
    
        handler.banner = 'purview ftp server ready'
        address = (host, port)
        self.server = FTPServer(address, handler)
        
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5
        
    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.close_all()

if __name__ == '__main__':
    server = VideoServer('127.0.0.1', 8888)
    server.run()
