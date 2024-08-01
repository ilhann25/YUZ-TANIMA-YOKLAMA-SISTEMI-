import cv2  
import pickle  
import numpy as np  # NumPy kütüphanesir
import os  

# Kamera bağlantısını aç
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("Hata: Kamera açılamadı.")
    exit()

# Yüz tespiti için önceden eğitilmiş sınıflandırıcıyı yükleme 
facesdetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Yüz verilerini depolamak için boş bir liste oluştur
faces_data = []
i = 0  # İterasyon sayacı

# Kullanıcıdan ad, soyad ve öğrenci numarası al
name = input("Adınızı giriniz: ")
surname = input("Soyadınızı giriniz: ")
student_number = input("Öğrenci numaranızı giriniz: ")

while True:
    # Kameradan bir kare al
    ret, frame = video.read()
    if not ret:
        print("Hata: Kare yakalanamadı.")
        break

    # Kareyi gri tonlamaya çevir
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Yüz tespiti yapma 
    faces = facesdetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Yüz bölgesini kırp ve boyutlandırma
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50))

        #100 yüz verisi toplandıysa veya her 5 karede bir veri toplanıyor
        if len(faces_data) < 100 and i % 5 == 0:
            faces_data.append(resized_img)
        i += 1

        # Kare üzerine yüz sayısını ve dikdörtgen çiz
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)

    # Videoyu ekrana göster
    cv2.imshow('Video', frame)

    # 'q' tuşuna basılırsa veya 100 yüz verisi toplandıysa programı bittirrr
    k = cv2.waitKey(1)
    if k == ord('q') or len(faces_data) == 100:
        break

# Kamera bağlantısını kapat
video.release()
cv2.destroyAllWindows()

# Yüz verilerini NumPy dizisine dönüştür ve boyutlandır
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(len(faces_data), -1)

# faces_data.pkl dosyasına yüz verilerini ve öğrenci numaralarını kaydet
if 'faces_data.pkl' not in os.listdir('data/'):
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces_data, f)
else:
    try:
        # faces_data.pkl dosyasını aç ve var olan yüz verilerini kontrol et
        with open('data/faces_data.pkl', 'rb') as f:
            existing_faces = pickle.load(f)

        # Yüz verilerinin boyutları eşleşmiyorsa hata ver
        if faces_data.shape[1] != existing_faces.shape[1]:
            print("Hata: Boyut uyumsuzluğu! faces_data ve existing_faces dizilerinin ikinci boyutları eşleşmiyor.")
        else:
            # Yüz verilerini birleştir ve dosyaya kaydet
            combined_faces = np.concatenate([existing_faces, faces_data], axis=0)
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(combined_faces, f)
    except EOFError:
        print("Hata: Dosya sonu hatası! 'faces_data.pkl' dosyasını düzeltin veya silin.")

# names.pkl dosyasına isim, soyisim ve öğrenci numaralarını kaydet
if 'names.pkl' not in os.listdir('data/'):
    student_info_list = [{'name': name, 'surname': surname, 'student_number': student_number}] * len(faces_data)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(student_info_list, f)
else:
    with open('data/names.pkl', 'rb') as f:
        student_info_list = pickle.load(f)
    student_info_list += [{'name': name, 'surname': surname, 'student_number': student_number}] * len(faces_data)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(student_info_list, f)
