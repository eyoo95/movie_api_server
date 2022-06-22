from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector


class MovieListResource(Resource):
    # 영화 정보 리스트 API
    def get(self) :
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.        
        order = request.args['order']
        offset = request.args['offset']


        try :
            connection = get_connection()

            query = '''select r.movieId, m.title, count(r.userId) as reviews, avg(r.rating) as avgRating
                        from movie m
                        join rating r
                        on m.id = r.movie_id
                        group by m.title
                        order by '''+order+''' desc
                        limit '''+offset+''', 25;'''


            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query )

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()

            i = 0
            for record in result_list:
                result_list[i]['avgRating'] = float(record['avgRating'])
                i = i + 1
            

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':20}, 503

        return { "result" : "success",
                "count" : len(result_list),
                "result_list" : result_list} , 200

class MovieInfoResource(Resource):
        # 영화 상세정보 화면 API
        def get(self, movie_id) :
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.        

            try :
                connection = get_connection()

                query = '''select r.movie_id, m.title, m.year, m.attendance, avg(r.rating) as avgRating
                            from movie m
                            join rating r
                            on m.id = r.movieId and r.movieId = %s
                            group by r.movieId;'''

                record = (movie_id,)

                # select 문은 dictionary = True를 해준다.
                cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

                cursor.execute(query,record )

                # select문은 아래 함수를 이용해서 데이터를 가져온다.
                result_list = cursor.fetchall()

                i = 0
                for record in result_list:
                    result_list[i]['avgRating'] = float(record['avgRating'])
                    result_list[i]['year'] = record['year'].isoformat()
                    i = i + 1
                

                cursor.close()
                connection.close()

            except mysql.connector.Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {"error":str(e), 'error_no':20}, 503

            return { "result" : "success",
                    "result_list" : result_list} , 200

class MovieRatingResource(Resource):
        # 해당영화 리뷰 정보를 보여주는 API
        def get(self, movie_id) :
            offset = request.args['offset']      
            try :
                connection = get_connection()

                query = '''select u.name, u.gender, r.rating
                            from movie m
                            join rating r
                            on m.id = r.movieId and r.movieId = %s
                            join user u
                            on r.userId = u.id
                            limit '''+offset+''', 25;'''

                record = (movie_id,)

                # select 문은 dictionary = True를 해준다.
                cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

                cursor.execute(query,record )

                # select문은 아래 함수를 이용해서 데이터를 가져온다.
                result_list = cursor.fetchall()

                # i = 0
                # for record in result_list:
                #     result_list[i]['avg_rating'] = float(record['avg_rating'])
                #     i = i + 1
                

                cursor.close()
                connection.close()

            except mysql.connector.Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {"error":str(e), 'error_no':20}, 503

            return { "result" : "success",
                    "count" : len(result_list),
                    "result_list" : result_list} , 200