import pandas as pd 
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector


class MovieReccomResource(Resource):
    # 영화 개인화 추천 API
    @jwt_required()
    def get(self) :
        # 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()
        # 추천을 위한 상관계수 데이터프레인을 읽어온다.
        df = pd.read_csv('data/movie_corr.csv', index_col= 'title')

        # 유저의 별점 정보를 DB에서 가져온다.
        try :
            connection = get_connection()

            query = '''select r.userId, r.movieId, m.title, r.rating
                        from rating r
                        join movie m
                        on r.movieId = m.id and r.userId = %s;'''

            record = (user_id,)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query, record)

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()
            

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':20}, 503

        # 가져온 유저 개인 rating 데이터를 데이터프레임으로 만든다.
        df_my_rating = pd.DataFrame(data=result_list)

        # 추천 영화를 저장할 빈 데이터 프레임을 만든다.
        similar_movie_list = pd.DataFrame()

        for i in range(len(df_my_rating)):
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlation']
            similar_movie_list = similar_movie_list.append(similar_movie)

        # 중복된 영화가 있을수있다. 중복된영화는 weight가 가장 큰 값으로 해준다.
        similar_movie_list.reset_index(inplace=True)
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서 별점을 남긴 영화는 제외해야한다.
        similar_movie_list = similar_movie_list.reset_index()

        # 내가이이미 본 영화제목만 가져온다.
        title_list = df_my_rating['title'].tolist()

        # similar_movie_list에 내가 본영화인 title_list를 제외하고 가져온다.
        # similar_movie_list['title'].isin(title_list)
        recommend_movie_list = similar_movie_list.loc[ ~similar_movie_list['title'].isin(title_list), ]

        return { "result" : "success",
                "movie_list" : recommend_movie_list.iloc[0:20,].to_dict('records')} , 200

class MovieRecomRealTimeRersource(Resource):
    # 실시간 영화 개인화 추천 API
    @jwt_required()
    def get(self) :
        # 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 유저의 별점 정보를 DB에서 가져온다.
        try :
            connection = get_connection()

            ####
            query = '''select r.userId, r.movieId, r.rating, m.title
                            from rating r
                            join movie m
                            on m.id = r.movieId;'''


            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query)

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()

            df = pd.DataFrame(data= result_list)
            matrix = df.pivot_table(index='userId', columns='title',values='rating')
            df = matrix.corr(min_periods=50)
            #####

            query = '''select r.userId, r.movieId, m.title, r.rating
                        from rating r
                        join movie m
                        on r.movieId = m.id and r.userId = %s;'''

            record = (user_id,)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query, record)

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':20}, 503

        # 가져온 유저 개인 rating 데이터를 데이터프레임으로 만든다.
        df_my_rating = pd.DataFrame(data=result_list)

        # 추천 영화를 저장할 빈 데이터 프레임을 만든다.
        similar_movie_list = pd.DataFrame()

        for i in range(len(df_my_rating)):
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlation']
            similar_movie_list = similar_movie_list.append(similar_movie)

        # 중복된 영화가 있을수있다. 중복된영화는 weight가 가장 큰 값으로 해준다.
        similar_movie_list.reset_index(inplace=True)
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서 별점을 남긴 영화는 제외해야한다.
        similar_movie_list = similar_movie_list.reset_index()

        # 내가이이미 본 영화제목만 가져온다.
        title_list = df_my_rating['title'].tolist()

        # similar_movie_list에 내가 본영화인 title_list를 제외하고 가져온다.
        # similar_movie_list['title'].isin(title_list)
        recommend_movie_list = similar_movie_list.loc[ ~similar_movie_list['title'].isin(title_list), ]

        return { "result" : "success",
                "movie_list" : recommend_movie_list.iloc[0:20,].to_dict('records')} , 200