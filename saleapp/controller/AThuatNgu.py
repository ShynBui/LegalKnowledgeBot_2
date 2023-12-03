from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, current_user

from saleapp import app, jwt, dao

from flask import jsonify, request

from saleapp.dao import remove_escape_sequences
from saleapp.models import User
import os
import pandas as pd
import pandas as pd
from langchain.document_loaders import UnstructuredHTMLLoader
from pyvi import ViTokenizer, ViPosTagger
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



def get_nouns(sentence):
    nouns = []
    annotated_sentence = ViPosTagger.postagging(ViTokenizer.tokenize(sentence))
    # print(annotated_sentence[0])
    for i in range(len(annotated_sentence[0])):
        if annotated_sentence[1][i].startswith('N'):
            nouns.append(annotated_sentence[0][i])
    nouns =  list(set(nouns))
    return nouns

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

def is_in2(x, result):
    if (x in result):
        return 1
    return 0
def get_thuat_ngu_in_html(id):
    file_path = f"./data/bophapdiendientu/demuc/{id}.html"  # Đặt tên file HTML dựa trên id
    loader = UnstructuredHTMLLoader(file_path)
    data = loader.load()
    html = data[0].page_content
    html = html.replace('\n\\n', ' ')
    html = html.replace('\n', ' ')
    html = html.replace('\r', ' ')
    html = remove_escape_sequences(html)
    nouns = get_nouns(html)
    print(nouns)
    result = map(lambda x: x.replace("_", " ").lower(), nouns)
    result = list(set(result))
    data_thuat_ngu = pd.read_csv(
        './data/full_thuat_ngu_procesing_v3.csv')
    data_thuat_ngu['thuatngu_lower'] = data_thuat_ngu['thuatngu'].map(lambda x: x.lower().strip())
    words = data_thuat_ngu['thuatngu_lower'].map(lambda x: is_in(x, result))
    result_x = [x for x in words if x != -1]
    result_x = list(set(result_x))

    # data_thuat_ngu = pd.read_csv(
    #     './data/full_thuat_ngu_procesing_v3.csv')
    #

    #
    # words = data_thuat_ngu['thuatngu_lower'].map(lambda x: is_in(x, html))
    # result = [x for x in words if x != -1]
    # result = list(set(result))
    # print(result)
    #
    #

    data_thuat_ngu_temp = data_thuat_ngu.copy()
    data_thuat_ngu_temp['drop'] = data_thuat_ngu_temp['thuatngu_lower'].map(lambda x: is_in2(x, result_x))
    data_thuat_ngu_temp = data_thuat_ngu_temp[data_thuat_ngu_temp['drop'] != 0]

    result_dict = {"term": data_thuat_ngu_temp['thuatngu'].tolist(), "meaning": data_thuat_ngu_temp['mota'].tolist()}
    for term, meaning in result_dict.items():
        print(f"{term}: {meaning}")

    return jsonify(result_dict)
