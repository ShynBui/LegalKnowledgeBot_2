from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, current_user

from saleapp import app, jwt, dao

from flask import jsonify, request

from saleapp.models import User
import os
import pandas as pd

# @jwt_required()
def thuatngu_serializer(thuatngu):
    return {
        'id': thuatngu.id,
        'thuat_ngu': thuatngu.thuat_ngu,
        'mo_ta': thuatngu.mo_ta,
        'nguon': thuatngu.nguon,
        'link': thuatngu.link,
        'tinh': thuatngu.tinh,
        'label' : thuatngu.label
    }





def api_thuat_ngu():

   list_thuatngu = dao.get_all_thuat_ngu()
   if list_thuatngu is not None:
       serialized_list_thuat_ngu = [thuatngu_serializer(thuatngu) for thuatngu in list_thuatngu]
       return jsonify(serialized_list_thuat_ngu)


def api_tim_thuat_ngu():
    paragraph = request.json.get("paragraph")
    if paragraph is not None:
        source_path = os.path.join(app.root_path, 'data', 'full_thuat_ngu_procesing_v3.csv')
        data = pd.read_csv(source_path)
        words = []
        for x in data.iloc:
            if x['thuatngu'] and is_in(x['thuatngu'].lower().strip(), paragraph) != -1:
                words.append({'word': x['thuatngu'], 'mean': x['mota']})
        return jsonify(words), 200
    
    return jsonify({"msg": "empty"}), 204



def is_in(x, paragraph):
    if (x in paragraph):
        return x
    return -1