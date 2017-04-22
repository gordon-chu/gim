from flask import request, make_response, jsonify, send_file
from flask_restful import Resource, reqparse

from app.mod_api import models
from app.mod_api.resources import auth
from app.mod_api.resources import json_utils
from app.mod_api.resources import validators

from werkzeug.datastructures import CombinedMultiDict

def video_info(video):
    return {
        'video_id': video.v_id,
        'uploaded_on': video.uploaded_on,
        'tags': [t.name for t in video.tags],
        'upvotes': len([vt for vt in video.votes if vt.upvote]),
        'downvotes': len([vt for vt in video.votes if not vt.upvote]),
        'lat': video.lat,
        'lon': video.lon
        }

class VideoFiles(Resource):
    """The VideoFiles endpoint is for retrieval of specific video files (see the Videos endpoint for metadata retrieval and manipulation).
    
    This endpoint supports the following http requests:
    get -- returns the file associated with the given video id; authentication token required

    All requests require the client to pass the video id of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Given a video id, return the file associated with it. The user must provide a valid authentication token.

        Request: GET /VideoFiles/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
                  video file
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        video = models.Video.get_video_by_id(video_id)

        if video:
            vfile = send_file(video.retrieve(), mimetype='text/plain')
            return make_response(vfile, 200)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist')
            return make_response(jsonify(response), 404)

class Video(Resource):
    """The Videos endpoint is for retrieving and manipulating video metadata (see VideoFiles endpoint for retrieving the video file itself). The endpoint is implemented in the Video and Videos classes.

    This endpoint supports the following http requests:
    get -- returns metadata about the video; authentication token required
    patch -- updates the tags of the video; authentication token required
    delete -- deletes the video; authentication token required

    All requests require the client to pass the video of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Returns metadata for the video corresponding to the given video id. If the token is invalid, returns an error.

        Request: GET /Videos/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'video_id': 5,
                    'uploaded_on': 'Wed, 12 Apr 2017 21:14:57 GMT',
                    'tags': ['some', 'tags'],
                    'upvotes': 9001,
                    'downvotes': 666,
                    'lat': 60.97,
                    'lon': 20.48
                }
        }
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        video = models.Video.get_video_by_id(video_id)

        if video:
            response = json_utils.gen_response(data=video_info(video))
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist')
            return make_response(jsonify(response), 404)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def patch(self, video_id):
        # TODO: validate json input
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)

        video = models.Video.get_video_by_id(video_id)
        if video and video.u_id == u_id:
            post_data = request.get_json()
            if 'tags' in post_data:
                video.add_tags(post_data['tags'])                
                # TODO: voting
            response = json_utils.gen_response(success=True)
            return make_response(jsonify(response), 200)    
        else:
            response = json_utils.gen_response(success=False, msg='you do not own a video with this id')
            return make_response(jsonify(response), 401)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def delete(self, video_id):
        """Deletes a video. Requesting user must own the video in order to delete it. If the auth token is invalid, returns an error.

        Request: DELETE /Videos/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        
        video = models.Video.get_video_by_id(video_id)
        if video and video.u_id == u_id:
            video.delete()
            response = json_utils.gen_response(success=True)
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg='you do not own a video with this id')
            return make_response(jsonify(response), 401)

class Videos(Resource):
    """The Videos endpoint is for retrieving and manipulating video metadata (see VideoFiles endpoint for retrieving the video file itself). The endpoint is implemented in the Video and Videos classes.

    This endpoint supports the following http requests:
    get -- returns metadata for some number of videos; authentication token required
    post -- uploads a video and returns its video id; authentication token required
    """

    @auth.require_auth_token
    def get(self):
        """Uploads a video to the database and returns a new video id. If the auth token is invalid, returns an error.

        Request: GET /Videos?lat=22.0&lon=67.8&tag=t1&tag=t2&sortBy=popular
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'videos': 
                        [
                            {
                                'video_id': 5,
                                'uploaded_on': ,
                                'tags': ['tiger', ...],
                                'upvotes': 46,
                                'downvotes': 0
                            }, 
                            ...
                        ]
                }
        }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('lat', type=float, required=True,
                            help='Latitude required')
        parser.add_argument('lon', type=float, required=True,
                            help='Longitude required')
        parser.add_argument('tag', action='append')
        parser.add_argument('limit', type=int)
        parser.add_argument('offset', type=int)
        parser.add_argument('sortBy', type=str)
        args = parser.parse_args()
        
        lat = args['lat']
        lon = args['lon']
        tags = args.get('tag', [])
        limit = args.get('limit', 5)
        offset = args.get('offset', 0)
        sort_by = args.get('sortBy', 'popular')

        # check for illegal query coordinates
        if lat > 90 or lat < -90 or lon > 180 or lon < -180:
            response = json_utils.gen_response(success=False, msg='Illegal coordinates entered')
            return make_response(jsonify(response), 400)

        videos = models.Video.search(lat, lon, tags, limit, offset, sort_by)
        video_infos = [video_info(v) for v in videos]
        response = json_utils.gen_response(data={'videos': video_infos})
        return make_response(jsonify(response), 200)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def post(self):
        """Uploads a video to the database and returns a new video id. If the auth token is invalid, returns an error.

        Request: POST /Videos
                 Authorization: Bearer auth_token
                 Content-type: multipart/form-data
        {
            'file': <video_file, filename.mov>,
            'lat': 57.2,
            'lon': 39.4,
            'tags': ['soulja', 'boy', 'tell', 'em']
        }
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'video_id': 7
                }
        }
        """
        form = validators.VideoUploadForm(CombinedMultiDict((request.files, request.form)))
        if not form.validate():
            response = json_utils.gen_response(success=False, msg=form.errors)
            return make_response(jsonify(response), 400)

        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        
        vfile = request.files.get('file')
        post_data = request.form
        lat = post_data.get('lat')
        lon = post_data.get('lon')
        tags = post_data.getlist('tags')

        video = models.Video(vfile, u_id, lat, lon)
        video.commit(insert=True)
        video.add_tags(tags)

        response = json_utils.gen_response(data={'video_id': video.v_id})
        return make_response(jsonify(response), 200)
