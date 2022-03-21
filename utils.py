import sqlite3
import numpy as np
import base64
import cv2

from pyArango.connection import *
conn = Connection(username="root", password="")

db = conn["_system"]

def matrix2string(m):
    string = ' '.join(str(x) for x in m)
    
    string = string.encode('ascii')
    base64_bytes = base64.b64encode(string)
    encoded_auth_code = base64_bytes.decode('ascii')
    return encoded_auth_code

def string2matrix(m):
    
    base64_bytes = m.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    matrix = message_bytes.decode('ascii')

    matrix = np.array([int(x) for x in matrix.split()])
    return matrix


def check_user(user):
    if (user['name'] == '' or user['password'] == ''  or user['pub_keys']['pubKey_e'] == '' or user['pub_keys']['pubKey_n'] == '') :
        return False
    else:
        return True


def insert_user_SQL(user):
    conn = sqlite3.connect('DB/database.db')
    
    sql = '''
    INSERT INTO user(name, password, pubKey_e, pubKey_n) 
    VALUES (?, ?, ?, ?)
    '''
    conn.execute(sql, (user['name'], user['password'],
                       user['pub_keys']['pubKey_e'], 
                       user['pub_keys']['pubKey_n']))
    conn.commit()

    sql = '''
    SELECT u.id 
    from user u
    where u.name=? and u.password=? and u.pubKey_e=? and u.pubKey_n=?
    '''
    id = conn.execute(sql, (user['name'], user['password'],
                       user['pub_keys']['pubKey_e'], 
                       user['pub_keys']['pubKey_n'])).fetchone()
                    
    conn.close()
    return id[0]

def insert_user(user):
    new_user = {"name": user['name'], 
                "password": user['password'], 
                "pubKey_e": user['pub_keys']['pubKey_e'],
                "pubKey_n": user['pub_keys']['pubKey_n'],
                "images": []}
    bind = {"doc": new_user}

    aql = '''
    insert @doc into users let newdoc = NEW return newdoc._key
    '''
    queryResult = db.AQLQuery(aql, rawResults = True, bindVars=bind)
    return queryResult[0]

def sign_in_SQL(user_info):
    id = user_info['id']
    password = user_info['password']

    conn = sqlite3.connect('DB/database.db')
    sql ='''
    SELECT id, password, name FROM user WHERE id = ?
    '''
    user = conn.execute(sql, (id,)).fetchone()
    conn.close()
    if user:
        if user[1] == password:
            return user[2]
        else:
            return False
    else:
        return False

def sign_in(user_info):
    id = user_info['id']
    password = user_info['password']
    bind = {'id': id}
    aql = '''
    for user in users
        filter user._key == @id
        return {_key : user._key, password: user.password, name: user.name}
    '''
    user = db.AQLQuery(aql, bindVars=bind, rawResults = True)[0]
    if user:
        if user['password'] == password:
            return user['name']
        else:
            return False
    else:
        return False


def get_list_img_SQL(user_info):
    id = user_info['id']
    
    conn = sqlite3.connect('DB/database.db')
    sql = '''
    SELECT id, name from image where id_user=?
    '''
    list_info_img = conn.execute(sql, (id,)).fetchall()
    conn.close()
    ans = []
    for row in list_info_img:
        temp = dict()
        temp['id'] = row[0]
        temp['name'] = row[1]
        ans.append(temp)
    return ans
def get_list_img(user_info):
    id = user_info['id']
    bind = {"id": id}
    aql = '''
    for user in users 
        filter user._key == @id
        return user.images
    '''
    id_img = db.AQLQuery(aql, bindVars=bind, rawResults=True)[0]
    id_img = [i for i in id_img]
    
    aql = '''
    for image in images 
        return {id : image._key, name : image.name }
    '''
    list_img = db.AQLQuery(aql,rawResults = True)
    list_img = [image for image in list_img]
    
    ans = []
    for image in list_img:
        if image['id'] in id_img:
            ans.append(image)
    return ans  
     

def upload_img_SQL(id_user, img):
    img_data = img['img_data']
    img_temp = img['img_temp']
    key_order = img['key_order']
    name = img['name']
    img_shape = img['img_shape']

    conn = sqlite3.connect('DB/database.db')
    sql='''
    SELECT * from user where id=?
    '''
    user = conn.execute(sql, (id_user, )).fetchone()
    if not user:
        return False
    
    sql = '''
    INSERT INTO image(id_user, img_data, img_temp, key_order,name, img_shape)
    VALUES(?, ?, ?, ?, ?, ?)
    '''
    conn.execute(sql, (id_user, img_data, img_temp, key_order, name, img_shape))
    conn.commit()
    return True

def upload_img(id_user, img):
    img_data = img['img_data']
    img_temp = img['img_temp']
    key_order = img['key_order']
    name = img['name']
    img_shape = img['img_shape']
    bind = {"id": id_user}
    aql = '''
    for user in users
        filter user._key == @id
        return user
    '''
    user = db.AQLQuery(aql, bindVars=bind, rawResults = True)[0]
    if not user:
        return False
    bind = {"name": name, "img_data": img_data, "img_temp": img_temp, "img_shape": img_shape, "key_order": key_order}
    aql = '''
    insert {name : @name, img_data: @img_data, img_temp: @img_temp, img_shape: @img_shape, key_order: @key_order } into images
    let ans = NEW
    return ans._key
    '''
    new_img_id = db.AQLQuery(aql, bindVars=bind, rawResults = True)[0]
 
    bind = {"id": new_img_id, "user_id": id_user}
    aql = '''
    for user in users
        filter user._key == @user_id
        update user with{
            images : push(user.images, @id)
        } in users
    '''
    resultAQL = db.AQLQuery(aql, bindVars=bind, rawResults = True)
    return True

def download_img_SQL(info):
    id = info['id']
    id_user = info['id_user']

    conn = sqlite3.connect('DB/database.db')
    sql ='''
    SELECT * from image where id=? and id_user=?
    '''
    img = conn.execute(sql,(id, id_user)).fetchone()
    
    conn.close()
    if not img:
        return None

    img_data = img[2]
    img_temp = img[3]
    key_order = img[4]
    img_name = img[5]
    img_shape = img[6]
    shape_str = img_shape[:]

    img_shape = string2matrix(img_shape)
    img_shape = tuple(img_shape)

    img_data = string2matrix(img_data)
    img_data = img_data.reshape(img_shape)


    img_temp = string2matrix(img_temp)
    key_order = string2matrix(key_order)

    img_temp = img_temp.reshape(img_data.shape).astype(np.int32)

    key_order = np.argsort(key_order)
    img_data = img_data[key_order]


    new_img = img_temp*255 + img_data
    
    new_img = new_img.ravel()
    new_img = matrix2string(new_img)
    return {'img':new_img, 'shape': shape_str, 'name': img_name}

def download_img(info):
    id = info['id']
    id_user = info['id_user']
    bind = {'id': id}
    aql ='''
    for image in images
        filter image._key == @id
        return {name: image.name, 
                img_data: image.img_data,
                img_temp: image.img_temp,
                img_shape: image.img_shape,
                key_order: image.key_order}
    '''
    img = db.AQLQuery(aql, bindVars=bind, rawResults = True)[0]

    if not img:
        return None

    img_data = img['img_data']
    img_temp = img['img_temp']
    key_order = img['key_order']
    img_name = img['name']
    img_shape = img['img_shape']
    shape_str = img_shape[:]

    img_shape = string2matrix(img_shape)
    img_shape = tuple(img_shape)

    img_data = string2matrix(img_data)
    img_data = img_data.reshape(img_shape)


    img_temp = string2matrix(img_temp)
    key_order = string2matrix(key_order)

    img_temp = img_temp.reshape(img_data.shape).astype(np.int32)

    key_order = np.argsort(key_order)
    img_data = img_data[key_order]


    new_img = img_temp*255 + img_data
    
    new_img = new_img.ravel()
    new_img = matrix2string(new_img)
    return {'img':new_img, 'shape': shape_str, 'name': img_name}
def download_img_all(info):
    id_user = info['id_user']

    bind = {'id': id_user}
    aql = '''
    for user in users
        filter user._key == @id
        return user.images
    '''

    imgs_id = db.AQLQuery(aql, bindVars=bind, rawResults = True)[0]   
    imgs = []
    for img_id in imgs_id:
        bind = {'id': img_id}
        aql = '''
        for image in images
            filter image._key == @id
            return {name: image.name, 
                    img_data: image.img_data,
                    img_temp: image.img_temp,
                    img_shape: image.img_shape,
                    key_order: image.key_order}
        '''
        img = db.AQLQuery(aql,bindVars=bind, rawResults = True)[0]
        imgs.append(img)
    if  len(imgs) == 0:
        return None
    data_imgs = []
    for img in imgs:

        img_data = img['img_data']
        img_temp = img['img_temp']
        key_order = img['key_order']
        img_name = img['name']
        img_shape = img['img_shape']
        shape_str = img_shape[:]

        img_shape = string2matrix(img_shape)
        img_shape = tuple(img_shape)

        img_data = string2matrix(img_data)
        img_data = img_data.reshape(img_shape)


        img_temp = string2matrix(img_temp)
        key_order = string2matrix(key_order)

        img_temp = img_temp.reshape(img_data.shape).astype(np.int32)

        key_order = np.argsort(key_order)
        img_data = img_data[key_order]


        new_img = img_temp*255 + img_data
        
        new_img = new_img.ravel()
        new_img = matrix2string(new_img)
        data_imgs.append ({'img':new_img, 'shape': shape_str, 
                           'name': img_name})
    
    return data_imgs

def share_img(info):
    pass

def get_pubkey_SQL(id):
    conn = sqlite3.connect('DB/database.db')
    sql ='''
    SELECT pubKey_e, pubKey_n From user where id=?
    '''
    pub_keys = conn.execute(sql, (id, )).fetchone()
    conn.close()
    return pub_keys
def get_pubkey(id):
    bind ={'id': id}
    aql = '''
    for user in users
        filter user._key == @id
        return {pubKey_e : user.pubKey_e, 
                pubKey_n : user.pubKey_n}
    '''
    pub_keys = db.AQLQuery(aql, bindVars=bind, rawResults = True)[0]
    pub_keys = [pub_keys['pubKey_e'], pub_keys['pubKey_n']]
    return pub_keys

if __name__ == '__main__':
    #download_img({'id': 1, 'id_user': 1})
    pass