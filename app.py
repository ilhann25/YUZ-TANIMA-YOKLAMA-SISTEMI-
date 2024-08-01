import streamlit as st
import os
import pandas as pd

def main():
    st.title("Ders Hafta Bilgileri Görüntüleme")

    # Ders adını al
    class_name = st.text_input("Ders Adı:")
    class_name = class_name.strip()

    if class_name:
        try:
            # Ders klasöründeki tüm dosyaları listele
            folder_path = f"Attendance/{class_name}/"
            files = os.listdir(folder_path)

            # Ders adına uygun dosyaların isimlerini görüntüle
            st.subheader(f"{class_name} Dersine Ait Tüm Hafta Dosyaları:")
            for file in files:
                st.write(file)

            # Bir dosya seçilirse, içeriğini görüntüle
            selected_file = st.selectbox("Dosyayı Seç:", files)
            if selected_file:
                file_path = os.path.join(folder_path, selected_file)
                
                # Ayırıcıyı belirt
                df_week_data = pd.read_csv(file_path, sep=',')
                
                st.subheader(f"{selected_file} Dosyasının İçeriği:")
                
                # DataFrame'i görüntüle
                st.dataframe(df_week_data)
        except FileNotFoundError:
            st.error(f"{class_name} dersine ait dosya bulunamadı.")

if __name__ == "__main__":
    main()
