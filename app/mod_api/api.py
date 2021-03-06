# Import flask dependencies
from flask import Blueprint
from flask_restful import Api

from resources import videos, users, auth, hof, banned_videos
from app import db

mod_api = Blueprint('api', __name__, url_prefix='/api')
api_v1 = Api(mod_api)

# videos routes
api_v1.add_resource(videos.Videos, '/Videos')
api_v1.add_resource(videos.Video, '/Videos/<int:video_id>')
api_v1.add_resource(videos.VideoFiles, '/VideoFiles/<int:video_id>')
api_v1.add_resource(videos.Thumbnails, '/Thumbnails/<int:video_id>')

# banned_videos routes
api_v1.add_resource(banned_videos.BannedVideo, '/BannedVideos/<int:video_id>')
api_v1.add_resource(banned_videos.BannedVideoFiles, '/BannedVideoFiles/<int:video_id>')

# hall of fame routes
api_v1.add_resource(hof.HallOfFame, '/HallOfFame')
api_v1.add_resource(hof.HallOfFameFiles, '/HallOfFameFiles/<int:video_id>')
api_v1.add_resource(hof.HallOfFameThumbnails, '/HallOfFameThumbnails/<int:video_id>')

# user routes
api_v1.add_resource(users.Users, '/Users')
api_v1.add_resource(users.User, '/Users/<int:user_id>')

# authentication routes
api_v1.add_resource(auth.Register, '/Auth/Register')
api_v1.add_resource(auth.Confirm, '/Auth/Confirm/<string:token>')
api_v1.add_resource(auth.Login, '/Auth/Login')
api_v1.add_resource(auth.Status, '/Auth/Status')
api_v1.add_resource(auth.Logout, '/Auth/Logout')

