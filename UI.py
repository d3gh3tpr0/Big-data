import client


if __name__ == '__main__':
    print("DH KHOA HOC TU NHIEN - MA HOA MAT MA")
    print("HE THONG LUU TRU ANH TRUC TUYEN")
    info_dev = client.get_page()['data']
    devs = info_dev['students']
    for dev in devs:
        print("\tTen: {}     MSSV:{}".format(dev['name'], dev['id']))
    print("\tTen nhom: ", info_dev['name_group'])
    print("\n"*3)
    
    
    while True:
        print("1.Dang nhap")
        print("2.Dang ky")
        print("3.Thoat")
        choose = int(input("Nhap vao lua chon:\t"))
        while(choose<1 or choose>3):
            choose = int(input("Lua chon khong hop le, vui long nhap lai:\t"))

        if choose == 2:
            name = input("Nhap vao ten cua ban:\t")
            password = input("Nhap vao password cua ban:\t")
            data = {"name": name, "password": password}
            req_data = client.sign_up(data)
            if not req_data:
                print("Dang ky that bai")
            else:
                print("ID de dang nhap cua ban la: ", req_data['id'])

        if choose == 1:
            id = input("Nhap vao ID cua ban:\t")
            password = input("Nhap vao mat khau cua ban:\t")
            print(""*3)
            req_data = client.sign_in({"id": id, "password": password})
            if not req_data:
                print("Dang nhap that bai")
                continue
            else:
                print("Chao mung {} den voi he thong luu tru anh truc tuyen".format(req_data['name']))
                print('Danh sach anh cua ban: ')
                print('ID\tImage\'s name')
                for img in req_data['list_info_img']:
                    print('{}\t{}'.format(img['id'], img['name']))
                
            print(""*2)
            

            print("Vui long nhap khoa cua ban de su dung cac tinh nang!")
            path_pub = input('Nhap vao duong dan toi file khoa cong khai cua ban:\t')
            path_pri = input('Nhap vao duong dan toi file khoa bi mat cua ban:\t')
            print("")

            pub_keys = open(path_pub, 'r').readline()
            pri_keys = open(path_pri, 'r').readline()

            while(True):
                print("1.Tai anh len")
                print("2.Tai 1 anh")
                print("3.Tai toan bo anh")
                print("4.Chia se anh")
                print("5.Dang xuat\n")

                choose_feature = int(input("Nhap vao chuc nang ban muon thuc hien:\t"))
                while(choose_feature<1 or choose_feature>5):
                    choose_feature = int(input("Nhap sai chuc nang, vui long nhap lai:\t"))

                if choose_feature == 5:
                    break

                if choose_feature == 1:
                    message_upload = client.upload_img(pub_keys, pri_keys, id)
                    print(message_upload)  
                    print(""*2)

                if choose_feature == 2:
                    message_download = client.download_img(pub_keys, pri_keys, id)  
                    print(message_download)
                    print(""*2)

                if choose_feature == 3:
                    message_download = client.download_img_all(pub_keys, pri_keys, id)  
                    print(message_download)
                    print(""*2)

                if choose_feature == 4:
                    message_share = client.share_img(pub_keys, pri_keys, id)
                    print(message_share)
                    print(""*2)
        if choose == 3:
            break


