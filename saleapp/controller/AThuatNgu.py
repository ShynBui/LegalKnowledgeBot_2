from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, current_user

from saleapp import app, jwt, dao

from flask import jsonify, request

from saleapp.models import User
import os
import pandas as pd
from pyvi import ViTokenizer, ViPosTagger
import requests


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


API_URL = "https://api-inference.huggingface.co/models/ShynBui/text_classification"
headers = {"Authorization": "Bearer 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"}
            



def api_tim_thuat_ngu():
    paragraph = request.json.get("paragraph")
    if paragraph is not None:
        nouns = get_nouns(paragraph)
        result = map(lambda x: x.replace("_", " ").lower(), nouns)
        result = list(set(result))

        source_path = os.path.join(app.root_path, 'data', 'full_thuat_ngu_procesing_v3.csv')
        data = pd.read_csv(source_path)
        data['thuatngu_lower'] = data['thuatngu'].map(lambda x : x.lower().strip())

        words = data['thuatngu_lower'].map(lambda x : is_in(x, result))
        
        terminology_dict = dict(zip(data['thuatngu_lower'], data['mota']))
        result_x = []
        non_existed_word = []
        for n in words:
            if n in terminology_dict:
                result_x.append({'word': n, 'mean': terminology_dict[n]})
            else:
                non_existed_word.append(n)
                
        all_sentences = paragraph.split('.')
        all_sentences = list(map(lambda x : x.strip().lower(), all_sentences))
        find_data = find_sentence_with_word(all_sentences, result)

        find_data['drop'] = find_data['word'].map(lambda x : -1 if (x in non_existed_word) else 1)
        find_data = find_data[find_data['drop'] != -1]
        
        find_data['drop'] = find_data.apply(lambda x : check_at_start_of_sentence(x['word'] , x['sentence']), axis = 1)
        find_data = find_data[find_data['drop'] != 0]
        find_data['sentence_en'] = find_data['sentence'].map(lambda x : (ViTokenizer.tokenize(x) + '.'))
        import time
        
        result_non_existed = []
        
        for i in find_data['sentence_en']:
            output = query({
            "inputs": i.strip()
            })
            while "error" in output:
                print('fail')
                time.sleep(1)
                output = query({
            "inputs": i.strip()
            })
            result_non_existed.append({i: output})
        
        
        return jsonify({"existed-words": result_x, "non-existed-words": result_non_existed}), 200    
    return jsonify({"msg": "empty"}), 204



def is_in(x, paragraph):
    if (x in paragraph):
        return x
    return -1


def check_at_start_of_sentence(word, sentence):
    # Kiểm tra xem từ đó có nằm ở vị trí đầu tiên của câu không
    if sentence.startswith(word):
        return 1
    return 0


def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()



def get_nouns(sentence):
    nouns = []
    annotated_sentence = ViPosTagger.postagging(ViTokenizer.tokenize(sentence))
    # print(annotated_sentence[0])
    for i in range(len(annotated_sentence[0])):
        if annotated_sentence[1][i].startswith('N'):
            nouns.append(annotated_sentence[0][i])
    nouns =  list(set(nouns))
    return nouns


def find_sentence_with_word(sentences, words):
    result_words = []
    result_sentenecs = []
    for word in words:
        for s in sentences:
            if word in s:
                result_words.append(word)
                result_sentenecs.append(s)
    return pd.DataFrame({'word' : result_words,
                        'sentence': result_sentenecs})