from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, current_user

from saleapp import app, jwt, dao

from flask import jsonify, request

from saleapp.models import User, UserRole
from saleapp import embeddings
import os

from langchain.text_splitter import CharacterTextSplitter
from pyvi import ViTokenizer
import requests
from langchain.vectorstores import Chroma


API_URL = "https://api-inference.huggingface.co/models/ShynBui/vie_qa"
headers = {"Authorization": "Bearer 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"}


def tin_nhan_serializer(tin_nhan):
    return {
        'id': tin_nhan.id,
        'noi_dung': tin_nhan.noi_dung,
        'thoi_gian_tao': tin_nhan.thoi_gian_tao,
        'user_id': tin_nhan.user_id,
        'nguon': tin_nhan.nguon
    }



def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


@jwt_required()
def get_tin_nhan_api():
    tin_nhan_list = dao.get_tin_nhan_by_user_id(current_user.id)
    serialized_list_tin_nhan = [tin_nhan_serializer(tin_nhan) for tin_nhan in
                                          list_tin_nhan]
    return jsonify(serialized_list_tin_nhan)



@jwt_required()
def add_tin_nhan_api():
    noi_dung = request.json.get('noi_dung')
    de_muc_id = request.json.get('de_muc_id')

    path = os.path.join(app.root_path, 'data', de_muc_id)
    if noi_dung and not noi_dung.endswith('?'):
        noi_dung += '?'

    if os.path.exists(path):
        chroma_db = Chroma(persist_directory=(path), embedding_function=embeddings)
        retriever = chroma_db.as_retriever(search_type="mmr")
        
        
        docs = retriever.get_relevant_documents(msg)
        result = []
        
        import time
        for i in docs:
            context = ViTokenizer.tokenize(i.page_content)
            question = ViTokenizer.tokenize(msg)
            output = query({
            "inputs": {
                "question": question,
                "context": context
            },
            })
            
            while "error" in output:
                print('fail')
                time.sleep(1)
                step += 1
                output = query({
                "inputs": {
                    "question": question,
                    "context": context
                },
                })
                
            result.append({
                'answer': output['answer'],
                'scores': output['score'],
                'sources': i.metadata['source']
            })
        
        best_answer = {}
        for r in result:
            if not best_answer:
                best_answer = r
            elif r.get('scores') > best_answer.get('scores'):
                    best_answer = r
                                         
        if best_answer:
            tin_nhan_nguoi_dung = dao.add_tin_nhan(noi_dung=noi_dung, user_id=current_user.id)
            bot_message = dao.add_tin_nhan(noi_dung=noi_dung, user_id=current_user.id, nguon=best_answer.get('sources'))
            return jsonify(tin_nhan_serializer(bot_message)), 200
    return jsonify({}), 404