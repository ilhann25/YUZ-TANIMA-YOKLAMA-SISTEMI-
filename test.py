from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from gtts import gTTS
import pygame
from io import BytesIO

def speak(str1, lang='tr'):
    # Ses dosyasını çevirme
    tts = gTTS(str1, lang=lang)
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    # Ses dosyasını oynat
    pygame.mixer.init()
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(5)

#Kullanıcıdan derse ait bilgileri al
class_name = input("Ders adını girin: ")
lecturer_name = input("Dersin Hocası: ")
week_number = int(input("Kaçıncı hafta: "))

# Ders adına göre klasör oluştur(Attendance klasörünün içinde)
class_folder_path = f"Attendance/{class_name}"
if not os.path.exists(class_folder_path):
    os.makedirs(class_folder_path)

video = cv2.VideoCapture(0)# hangi kameranının kullanılacağı ,kamerayı aç
if not video.isOpened():
    print("Hata: Kamera açılamadı.")
    exit()

attendance = {}
COL_NAMES = ['NAME', 'SURNAME', 'STUDENT_NUMBER', 'LESSON', 'TIME', 'LECTURER', 'WEEK NUMBER']#csv ye kaydedilecek sütunlar yokalama bilgileri

#yüz tespiti sınıflandırıcısı
facesdetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Öğrenci bilgilerini ve yüz verilerini yükleme 
with open('data/names.pkl', 'rb') as f:
    student_info_list = pickle.load(f)
    LABELS = [student_info['student_number'] for student_info in student_info_list]

with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

LABELS = LABELS[:FACES.shape[0]]

# K-En Yakın Komşu (KNN) sınıflandırıcıyı oluşturma ve eğitme(yüz bilgisini öğrenciyle eşleştirme)
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

imgBackground = cv2.imread("background.png")#arka plan görüntüsü

# Daha önce kaydedilen öğrencilerin bir setini tutmak için
recorded_students = set()


# Ana döngü
while True:
    ret, frame = video.read()
    if not ret:
        print("Hata: Kare yakalanamadı.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facesdetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        # Yüz bölgesini kırpıp boyutlandır
        crop_img = frame[y:y + h, x:x + w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        resized_img = resized_img[:, :FACES.shape[1]]

        # Yüz tanıma kısmı
        output = knn.predict(resized_img)
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H-%M-%S")
        exist = os.path.isfile(f"{class_folder_path}/{class_name}_Week{week_number}.csv")

        # Kare üzerine çerçeve çizme
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)#kırmızı,(0,255,0(yeşil))
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)#mavi 
        cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)

        # Tanınan öğrenci bilgilerini alma
        person_info = output[0]  # Öğrenci numarası
        student_info = next((info for info in student_info_list if info['student_number'] == person_info), None)
        
        if student_info:
            # Ekrana ad ve soyadı yazdır
            text = f"{student_info['name']} {student_info['surname']}"
            cv2.putText(frame, text, (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

            key = cv2.waitKey(1) & 0xFF  # Son 8 biti elde etmek için maskeleme
            if key == ord('q'):
                break  # 'q' tuşuna basıldığında programdan çık

            if key == ord('o'):
                # 'o' tuşuna basıldığında her seferinde yoklama al
                attendance_key = (student_info['name'], student_info['surname'], person_info, class_name, date, timestamp, lecturer_name, week_number)
                recorded_students.add(attendance_key)
                attendance[attendance_key] = attendance_key

                # Dosya adını ders adına ve hafta numarasına göre düzenle
                csv_file_path = f"{class_folder_path}/{class_name}_{week_number}.Hafta.csv"

                # Dosyayı oluştur ve başlık satırını yaz
                if not os.path.isfile(csv_file_path):
                    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(COL_NAMES)

                # Öğrenciyi dosyaya yaz
                with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(attendance[attendance_key])

                # Sesli uyarı kısmı
                speak(f"{student_info['name']} {student_info['surname']} için yoklama alındı.", lang='tr')
        else:
            # Tanınmayan kişi olduğunda bilgiyi ekrana ve sesli olarak ekleyin
            unknown_text = "Bilinmeyen Kişi"
            cv2.putText(frame, unknown_text, (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            
            # Sesli uyarı
            speak("Bilinmeyen kişi algılandı.", lang='tr')

    # Arka plana kameradan alınan görüntüyü yerleştir
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow('Video', imgBackground)

    # 'q' tuşuna basılırsa döngüden çık
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

