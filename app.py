from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config
from flask_restful import Api
from resources.movie import MovieListResource, MovieInfoResource, MovieRatingResource, MoviefavoriteResource
from resources.user import UserRegisterResource, UserLoginResource, UserLogoutResource, UserMypageResource, UserFavoriteResource, jwt_blacklist
from resources.review import ReviewSearchResource, ReviewResource
from resources.recommend import MovieReccomResource
app = Flask(__name__)

# 환경변수 세팅
app.config.from_object(Config)

# JWT 토큰 라이브러리 만들기
jwt = JWTManager(app)

# 로그아웃된 토큰이 들어있는 set을 jwt에 알려준다
@jwt.token_in_blocklist_loader
def check_if_token_is_revoke(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist


api = Api(app)

# 경로와 resource(API 코드)를 연결한다.

api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')
api.add_resource(UserMypageResource, '/user/mypage')
api.add_resource(UserFavoriteResource, '/user/favorite')
api.add_resource(MovieListResource , '/movie')
api.add_resource(MovieInfoResource , '/movie/<int:movie_id>')
api.add_resource(MoviefavoriteResource , '/movie/<int:movie_id>/favorite')
api.add_resource(MovieRatingResource , '/movie/<int:movie_id>/ratings')
api.add_resource(ReviewSearchResource , '/review')
api.add_resource(ReviewResource , '/review/<int:movie_id>')
api.add_resource(MovieReccomResource , '/movie/recommend')

if __name__ == '__main__' :
    app.run()