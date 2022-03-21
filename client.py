import requests
import numpy as np
import cv2
import RSA
import base64


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



def get_page():
    url = "http://127.0.0.1:5000/"
    r = requests.get(url)
    ans = dict(r.json())
    return ans

def sign_up(data):
    url = "http://127.0.0.1:5000/sign-up"

    p, q, e, d, N = RSA.generateKeys(keysize=8)

    # data = {'name' :'Nam Anh', 
    #         'password':'hcmus2k1',
    #         'pubKey_e' : e,
    #         'pubKey_n' : N
    #     }

    data['pubKey_e'] = e
    data['pubKey_n'] = N

    file_prikeys = input("Nhap vao ten file khoa bi mat:\t")
    file_pubkeys = input("Nhap vao ten file khoa cong khai:\t")
    
    key_pri = str(p) + " " + str(q) + " " + str(d)
    key_pub = str(e) + " " + str(N)
    
    file_pri = open(file_prikeys, "w")
    file_pri.write(key_pri)
    file_pri.close()

    file_pub = open(file_pubkeys, 'w')
    file_pub.write(key_pub)
    file_pub.close()


    r = requests.post(url, data=data)

    req = dict(r.json())
    if req['statusCode'] == 401:
        return None
    
    verified_code = req['verified_code']
    
    base64_bytes = verified_code.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    encypted_code = message_bytes.decode('ascii')
 
    decoded_auth_code = RSA.decrypt(encypted_code, key_pri, N)
    
    data['decoded_auth_code'] = decoded_auth_code
    url = "http://127.0.0.1:5000/sign-up-auth"

    r = requests.post(url, data=data)
    req = dict(r.json())
    if req['statusCode'] == 401:
        return None
    else:
        return {"id": req["id"]}
    

def sign_in(user):
    url = "http://127.0.0.1:5000/sign-in"
    r = requests.get(url, params=user)
    req = dict(r.json())
    if req['statusCode'] == 401:
        return None
    else:
        return {"list_info_img": req["list_info_img"],
                "name": req["name"]}


#test upload-img
def upload_img(pub_keys, pri_keys, user_id):
    url = "http://127.0.0.1:5000/upload-img"

    img_path = input('Nhap vao duong dan toi file anh cua ban:\t')
    img = cv2.imread(img_path)

    img_name = img_path.split('/')[-1]

    img = img.astype('int')
    img_shape = img.shape

    def encrypt(x):
        copy = int(x)
        rsa = RSA.RSA(8, pub_keys)
        return rsa.encrypt_pixel(copy)

    func1 = np.vectorize(encrypt)
    encrypted_img = func1(img)
    img_temp, img_data = divmod(encrypted_img, 255)
    
    lock_order = np.random.permutation(len(img_data))
    img_data = img_data[lock_order]
 
    img_temp = img_temp.ravel()
    img_temp = matrix2string(img_temp)
    lock_order = matrix2string(lock_order)


    img_data = img_data.ravel()
    img_data = matrix2string(img_data)

    img_shape = list(img_shape)
    img_shape = matrix2string(img_shape)


    data = {'img_data':img_data,
            'img_temp':img_temp,
            'key_order':lock_order,
            'name': img_name, 
            'img_shape': img_shape}

    r = requests.post(url, data=data, params={'id': user_id})
    req = dict(r.json())
    if req['statusCode'] == 401:
        return "Tai anh {} len that bai".format(img_name)
    else:
        return "Tai anh {} len thanh cong".format(img_name)
    
def download_img(pub_keys, pri_keys, user_id):
    url = "http://127.0.0.1:5000/download-img"

    id_img = int(input("Nhap vao ID cua anh ma ban muon tai ve:\t"))
    print('Dang tai....')
    r = requests.get(url, params={'id': id_img,
                                  'id_user': user_id})

    req = dict(r.json())
    if req['statusCode'] == 200:
        data_img = req['data_image']
        
        img = data_img['img']
        shape = data_img['shape']
        img_name = data_img['name']

        new_img = string2matrix(img)
        shape = tuple(string2matrix(shape))
        new_img = new_img.reshape(shape)


        def decrypt(x):
            copy = int(x)
            rsa = RSA.RSA(8, pri_keys)
            N = int(pub_keys.split()[-1])
            rsa.N = N
            return rsa.decrypt_pixel(copy)


        func2 = np.vectorize(decrypt)
        

        original_img = func2(new_img)
        cv2.imwrite(img_name, original_img)
        return "Anh {} da duoc tai ve thanh cong".format(img_name)

    else:
        return "Anh tai ve that bai"
   
def download_img_all(pub_keys, pri_keys, user_id):
    url = "http://127.0.0.1:5000/download-img-all"

    r = requests.get(url, params={"id_user": user_id})
    req = dict(r.json())
    if req['statusCode'] == 200:

        def decrypt(x):
            copy = int(x)
            rsa = RSA.RSA(8, pri_keys)
            N = int(pub_keys.split()[-1])
            rsa.N = N
            return rsa.decrypt_pixel(copy)

        data_imgs = req['data_image']
        print("Dang tai....")
        for image in data_imgs:
            img = image['img']
            shape = image['shape']
            img_name = image['name']

            new_img = string2matrix(img)
            shape = tuple(string2matrix(shape))
            new_img = new_img.reshape(shape)

            func2 = np.vectorize(decrypt)
            
            original_img = func2(new_img)
            cv2.imwrite(img_name, original_img)
            print("Anh {} da duoc tai ve thanh cong".format(img_name))

        return "Tat ca anh cua ban da duoc tai ve hoan tat!"
    
    else:
        return "Anh tai ve that bai"

def share_img(pub_keys, pri_keys, id_src):
    id_img = int(input("Nhap vao ID anh ma ban muon share:\t"))
    id_des = int(input("Nhap vao ID nguoi ma ban muon share anh:\t"))
    
    url = "http://127.0.0.1:5000/download-img"

    print('Vui long cho....')
    r = requests.get(url, params={'id': id_img,
                                  'id_user': id_src})

    req = dict(r.json())
    if req['statusCode'] == 200:
        data_img = req['data_image']
        
        img = data_img['img']
        shape = data_img['shape']
        img_name = data_img['name']

        new_img = string2matrix(img)
        shape = tuple(string2matrix(shape))
        new_img = new_img.reshape(shape)


        def decrypt(x):
            copy = int(x)
            rsa = RSA.RSA(8, pri_keys)
            N = int(pub_keys.split()[-1])
            rsa.N = N
            return rsa.decrypt_pixel(copy)


        func2 = np.vectorize(decrypt)
        
        original_img = func2(new_img)
        
        url = "http://127.0.0.1:5000/share"
        r = requests.get(url, params={"id":id_des})
        #print(r.json())
        req = dict(r.json())
    
        if req['statusCode'] == 200:
            url = "http://127.0.0.1:5000/upload-img"


            def encrypt(x, keys):
                copy = int(x)
                rsa = RSA.RSA(8, keys)
                return rsa.encrypt_pixel(copy)

            func1 = np.vectorize(encrypt)
            encrypted_img = func1(original_img, req['pubkey_des'])
            img_temp, img_data = divmod(encrypted_img, 255)
            
            lock_order = np.random.permutation(len(img_data))
            img_data = img_data[lock_order]
        
            img_temp = img_temp.ravel()
            img_temp = matrix2string(img_temp)
            lock_order = matrix2string(lock_order)


            img_data = img_data.ravel()
            img_data = matrix2string(img_data)

            img_shape = list(shape)
            img_shape = matrix2string(img_shape)


            data = {'img_data':img_data,
                    'img_temp':img_temp,
                    'key_order':lock_order,
                    'name': img_name, 
                    'img_shape': img_shape}

            r = requests.post(url, data=data, params={'id': id_des})
            req = dict(r.json())
            if req['statusCode'] == 401:
                return "Chia se anh {} cho ID {} that bai".format(img_name, id_des)
            else:
                return "Chia se anh {} cho ID {} thanh cong".format(img_name, id_des)
        else:
            return "ID nguoi duoc gui khong hop le"
    else:
        return "Anh ban chon khong hop le!"
        

if __name__ == '__main__':
    pass






