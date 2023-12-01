import hashlib
import pandas as pd
from saleapp.models import *
import json
from saleapp import db


# def add_chuDe(filename):
#     df = pd.read_csv(filename)

#     return df['Value'].tolist(), df['Text'].tolist(), df['STT'].tolist()

# def import_chuDe():
#     value, text, stt = add_chuDe(
#         '/home/duchoang/Workspace/MaNguonMo2023/backend/saleapp/data/Chude_table.csv')

#     for i in range(len(value)):
#         db.session.add(ChuDePhapDien(id=value[i], stt=stt[i], text = text[i]))
#         db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        with open('/home/yuu/Documents/WorkSpace/nhomBTP/backend2/saleapp/data/output.json', 'r') as dataFile:
            dataObj = json.load(dataFile)
            
            index = {
                    0 : "Phan",
                    1 : "Chuong",
                    2 : "Muc",
                    3 : "TieuMuc",
                    4 : "Dieu",
                }
            
            listAll = []
            for chuDe in dataObj:
                topic = dataObj.get(chuDe)
                cd = ChuDePhapDien(id=topic.get('Value'), ten_chu_de=topic.get('Text'), stt=topic.get('STT'))
                listAll.append(cd)
                for deMuc in topic.get('children'):
                    dm = DeMucPhapDien(id=deMuc.get('Value'), ten_de_muc=deMuc.get('Text'), stt=deMuc.get('STT'), chu_de_phap_dien=cd)
                    if deMuc.get('children'):
                        for loop, items  in enumerate(deMuc.get('children')):
                            type = index.get(items.get('index'))
                            value = items.get('value')
                            cm = ChuongVaDieuPhapDien(id=value.get('ID') , ten=value.get('TEN'), stt=loop+1, mapc=value.get('MAPC'), de_muc_phap_dien=dm, chi_muc=type)
                            
                            if items.get('children'):
                                obj = items
                                objData = cm
                                while len(obj.get('children')) > 0:
                                    for loop, item in enumerate(obj.get('children')):
                                        type = index.get(item.get('index'))
                                        value = item.get('value')
                                        cmCo = ChuongVaDieuPhapDien(id=value.get('ID') , ten=value.get('TEN'), stt=loop+1, mapc=value.get('MAPC'), de_muc_phap_dien=dm, chi_muc=type, chuong_cha=cm)
                                    obj = item
                                    objData = cmCo                                
            db.session.add_all(listAll)
            db.session.commit()    
    