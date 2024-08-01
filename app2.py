import streamlit as st
import pandas as pd
import os

# DataFrame'leri tanımla
df_all_weeks = pd.DataFrame()
df_student_all_weeks = pd.DataFrame()

def main():
    global df_all_weeks, df_student_all_weeks  # df değişkenini global kapsama taşı

    # Kullanıcıdan ders adı ve hafta numarası al
    class_name = st.text_input("Dersin adını girin:")
    week_number = st.number_input("Kaçıncı hafta:", value=1)

    # CSV dosyalarını okuma işlemi
    folder_path = f"Attendance/{class_name}"
    csv_file_path = f"{folder_path}/{class_name}_{week_number}.Hafta.csv"

    try:
        # Dersin klasörü var mı kontrol et
        if os.path.exists(folder_path):
            # Tüm haftalara ait verileri birleştir
            df_all_weeks = pd.concat([pd.read_csv(os.path.join(folder_path, file)) for file in os.listdir(folder_path) if file.endswith(".csv")], ignore_index=True)
    
        else:
            st.warning(f"{class_name} sınıfı bulunamadı.")
            st.error("Uygulama durduruldu.")
            return

        # Belirtilen haftaya ait CSV dosyası var mı kontrol et
        if os.path.exists(csv_file_path):
            df_week = pd.read_csv(csv_file_path)
            st.success(f"{class_name}_{week_number}.Hafta verileri başarıyla yüklendi.")
        else:
            st.warning(f"{class_name}_{week_number}.Hafta.csv dosyası bulunamadı.")
            st.error("Uygulama durduruldu.")
            return

    except FileNotFoundError:
        st.warning(f"{class_name}_{week_number}.Hafta.csv dosyası bulunamadı.")
        st.error("Uygulama durduruldu.")
        return

    # Öğrenci adı-soyadı ile sorgulamaa
    st.sidebar.subheader("Öğrenci Adı-Soyadı ile Sorgula")
    student_name = st.sidebar.text_input("Öğrenci Adı:")
    student_surname = st.sidebar.text_input("Öğrenci Soyadı:")

    # Sorgulama  butonu
    if st.sidebar.button("Öğrenciyi Adı-Soyadı ile Sorgula"):
        query_student_by_name(class_name, student_name, student_surname, df_all_weeks)

    # Ana sayfada tüm dosyaları listeleyerek göster
    st.subheader(f"Öğrenci Tablosu - {class_name}_{week_number}.Hafta")
    st.write(df_week)

def query_student_by_name(class_name, student_name, student_surname, df_all_weeks):
    global df_student_all_weeks

    # Öğrenci adı ve soyadı var mı kontrol etme kısmıı
    if student_name and student_surname:
        # Öğrenciyi ad ve soyada göre filtrele
        queried_student = df_all_weeks[(df_all_weeks['NAME'] == student_name) & (df_all_weeks['SURNAME'] == student_surname)]
        if not queried_student.empty:
            # Öğrenci bulunduysa başarı mesajı
            student_number = queried_student['STUDENT_NUMBER'].values[0]
            st.success(f"{queried_student['NAME'].values[0]} {queried_student['SURNAME'].values[0]} adlı öğrenci derse katıldı.")

            # Tüm haftalardaki devam durumu bilgisini içeren DataFrame'i oluştur
            df_student_all_weeks = df_all_weeks[df_all_weeks['STUDENT_NUMBER'] == student_number].copy()
            df_student_all_weeks['Toplam Devam Durumu'] = df_student_all_weeks.groupby('WEEK_NUMBER')['ATTENDANCE'].transform('mean')

            # Öğrencinin devamsızlık kaydını bir tabloda göster
            st.sidebar.subheader(f"Öğrenci Devamsızlık Bilgisi - Tüm Haftalar ({class_name})")
            st.sidebar.table(df_student_all_weeks[['WEEK_NUMBER', 'Toplam Devam Durumu']].drop_duplicates())
        else:
            # Öğrenci bulunamadıysa uyarı
            st.sidebar.warning(f"{student_name} {student_surname} adlı öğrenci bulunamadı. Öğrenci derse gelmedi.")
    else:
        # Geçersiz giriş durumunda uyarı 
        st.sidebar.warning("Lütfen öğrenci adı ve soyadını girin.")

if __name__ == "__main__":
    main()
