from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector


class ReviewSearchResource(Resource):
    # 리뷰 작성할 영화검색 API
    def post(self) :

        data = request.get_json()

        offset = request.args['offset']

        try :
            connection = get_connection()

            query = '''select r.movieId, m.title, count(r.userId) as reviews, ifnull(avg(r.rating),0) as avgRating
                        from movie m
                        left join rating r
                        on m.id = r.movieId
                        where m.title like '%'''+data['keyword']+'''%'
                        group by m.id;
                        limit '''+offset+''', 25;'''

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query)

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

class ReviewResource(Resource):
    # 리뷰를 작성하는 API
    @jwt_required()
    def post(self, movie_id):
        data = request.get_json()

        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query =  '''insert 
                        into rating
                        (userId, movieId,rating)
                        value
                        (%s,%s,%s)'''

            record = (user_id, movie_id, data['rating'])

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

