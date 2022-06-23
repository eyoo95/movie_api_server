from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector


class MovieListResource(Resource):
    # 영화 정보 리스트 API
    @jwt_required()
    def get(self) :
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.  
        user_id = get_jwt_identity()
        
        order = request.args['order']
        offset = request.args['offset']


        try :
            connection = get_connection()

            query = '''select r.movieId, m.title, count(r.userId) as reviews,
                        ifnull(avg(r.rating),0) as avgRating,
                        if(f.userId is null, 0,1) as favorite
                        from movie m
                        left join rating r
                        on m.id = r.movieId
                        group by m.id
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

                query = '''select m.*, count(r.userId) as reviews, ifnull(avg(r.rating),0) as avgRating
                            from movie m
                            left join rating r
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
                    result_list[i]['createdAt'] = record['createdAt'].isoformat()
                    result_list[i]['updatedAt'] = record['updatedAt'].isoformat()
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

                query = '''select r.userId, u.name, u.gender, r.rating
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

class MoviefavoriteResource(Resource):
    # 즐겨찾기 추가하는 API
    @jwt_required()
    def post(self, movie_id):

        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query =  '''insert 
                        into favorite
                        (userId,movieId)
                        value
                        (%s,%s);'''

            record = (user_id, movie_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print (e)
            cursor.close()
            connection.close()
            return {'error':str(e)} , 503
        
        return {'result': 'success'}, 200

    # 즐겨찾기 삭제하는 API
    @jwt_required()
    def delete(self, movie_id ):
        user_id = get_jwt_identity()
        
        try : 
            # 1. DB에 연결
            connection = get_connection()            

            # 2. 쿼리문 만들기
            query = '''delete from favorite
                        where userId = %s and movieId = %s;'''

            record = (user_id,movie_id ) # 튜플형식


            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record )

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error':str(e)}, 503

        return {'result': 'success'} , 200             

