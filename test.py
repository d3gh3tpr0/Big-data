import sqlite3
import numpy as np 
import cv2
import base64
import RSA

def string2matrix(m):
    
    base64_bytes = m.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    matrix = message_bytes.decode('ascii')

    matrix = np.array([int(x) for x in matrix.split()])
    return matrix

conn = sqlite3.connect('DB/database.db')
sql ='''
SELECT * from image where id=?
'''
img = conn.execute(sql,(2, )).fetchone()

id_user = img[1]

conn.close()

img_data = img[2]
img_temp = img[3]
key_order = img[4]
img_shape = img[6]

img_shape = string2matrix(img_shape)
img_shape = tuple(img_shape)

img_data = string2matrix(img_data)
img_data = img_data.reshape(img_shape)

cv2.imwrite('hinhmahoa.jpg', img_data)

img_temp = string2matrix(img_temp)
key_order = string2matrix(key_order)

img_temp = img_temp.reshape(img_data.shape).astype(np.int32)

print('img_temp', img_temp)
print('lock_order', key_order)
print('img_data', img_data)

key_order = np.argsort(key_order)
img_data = img_data[key_order]


new_img = img_temp*255 + img_data

pri_keys = "241 173 20207"
N = 41693

def decrypt(x):
    copy = int(x)
    rsa = RSA.RSA(8, pri_keys)
    rsa.N = N
    return rsa.decrypt_pixel(copy)


func2 = np.vectorize(decrypt)

original_img = func2(new_img)
cv2.imwrite('djtconmemay.jpg', original_img)








