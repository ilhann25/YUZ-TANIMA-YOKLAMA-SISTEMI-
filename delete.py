import pickle
import numpy as np

delete_student_number = input("Silmek istediğiniz öğrenci numarasını giriniz: ")

# 1. Kullanıcıyı names.pkl dosyasından silme
try:
    with open('data/names.pkl', 'rb') as f:
        student_info_list = pickle.load(f)

    # Kullanıcıyı sil
    student_info_list = [student for student in student_info_list if student['student_number'] != delete_student_number]

    # Güncellenmiş listeyi dosyaya yaz
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(student_info_list, f)
except FileNotFoundError:
    print("Hata: 'names.pkl' dosyası bulunamadı.")
except Exception as e:
    print("Hata:", e)

# 2. Kullanıcıyı faces_data.pkl dosyasından silme
try:
    with open('data/faces_data.pkl', 'rb') as f:
        existing_faces = pickle.load(f)

    # Silmek istediğiniz kullanıcının indeksini bulun
    delete_index = [i for i, student in enumerate(student_info_list) if student['student_number'] == delete_student_number]
    
    # Kullanıcıyı sil
    existing_faces = np.delete(existing_faces, delete_index, axis=0)

    # Güncellenmiş diziyi dosyaya yaz
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(existing_faces, f)
except FileNotFoundError:
    print("Hata: 'faces_data.pkl' dosyası bulunamadı.")
except Exception as e:
    print("Hata:", e)
