import pandas as pd 
from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector


class ReccomandListResource(Resource):
    # 영화 정보 리스트 API
    @jwt_required()
    def get(self) :