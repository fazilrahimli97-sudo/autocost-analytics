import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AutoCost Analytics", layout="wide")
st.title("🚗 AutoCost Analytics — Ağıllı Avtomobil Seçim Paneli")
st.subheader("Büdcənizə və Aylıq Sürüşünüzə Uyğun Ən Sərfəli Maşının Təyini")

# 1. Baza Avtomobil Məlumat Matrisi (Azərbaycan bazarı üçün real verilənlər)
# yanacaq_tipi, seher_serfiyyat (L/100km), usta_indeksi (1-10), amortizasiya_nisbəti
car_database = {
    "Toyota Prius (XW30 - 2012)": {"tip": "Hibrid", "serfiyyat": 4.5, "usta": 3.5, "baza_qiymet": 14500, "yanacaq": "Aİ-92"},
    "Hyundai Elantra (1.6 Benzin - 2012)": {"tip": "Benzin", "serfiyyat": 8.5, "usta": 3.0, "baza_qiymet": 15000, "yanacaq": "Aİ-92"},
    "Mercedes-Benz C-Class (C220 CDI - 2008)": {"tip": "Dizel", "serfiyyat": 7.8, "usta": 5.0, "baza_qiymet": 15500, "yanacaq": "Dizel"},
    "Kia Ceed (1.4 Benzin - 2011)": {"tip": "Benzin", "serfiyyat": 8.0, "usta": 3.2, "baza_qiymet": 13800, "yanacaq": "Aİ-92"},
    "Opel Astra (1.3 CDTI - 2010)": {"tip": "Dizel", "serfiyyat": 6.5, "usta": 5.5, "baza_qiymet": 12500, "yanacaq": "Dizel"}
}

# 2. Cari Yanacaq Qiymətləri (AZN / Litr)
fuel_prices = {
    "Aİ-92": 1.10,
    "Dizel": 1.00,
    "Aİ-95 (Premium)": 1.60
}

# İnterfeys sütunları
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Sürücü Parametrləri")
    
    budget = st.number_input("Maksimum Avtomobil Alış Büdcəniz (AZN):", min_value=5000, max_value=100000, value=15000, step=500)
    monthly_km = st.slider("Aylıq Ortalama Sürəcəyiniz Məsafə (km):", min_value=200, max_value=10000, value=1500, step=100)
    monthly_max_maintenance = st.number_input("Maşına Ayıra Biləcəyiniz Maksimum Aylıq Xərc (AZN):", min_value=50, max_value=2000, value=250, step=10)
    transmission = st.selectbox("Sürət Qutusu Seçimi:", ["Fərqi yoxdur", "Avtomat", "Mexanika"])

with col2:
    st.header("📊 Maliyyə Analizi və Təxmin Nəticələri")
    
    results = []
    
    for car_name, info in car_database.items():
        # Büdcə yoxlanışı (Alış qiyməti uyğundurmu?)
        if info["baza_qiymet"] <= budget * 1.05: # 5% keçid payı ilə
            
            # 1. Aylıq Yanacaq Xərci Hesablanması
            fuel_type = info["yanacaq"]
            price_per_liter = fuel_prices[fuel_type]
            monthly_fuel_cost = (monthly_km * info["serfiyyat"] / 100) * price_per_liter
            
            # 2. Eksponent Model ilə Aylıq Ortalama Usta/Təmir Xərci
            # Usta indeksi yüksək olan və yaşlı maşınlar daha çox xərc çıxarır
            monthly_repair_cost = info["usta"] * 12.5 
            
            # 3. Ümumi Aylıq Sahiblik Xərci (TCO)
            total_monthly_cost = monthly_fuel_cost + monthly_repair_cost
            
            # Sərfəlilik İndeksi (Maksimum xərc limitinə görə optimallaşdırma)
            score = max(0, 100 - (total_monthly_cost / monthly_max_maintenance * 50))
            
            results.append({
                "Avtomobil": car_name,
                "Tip": info["tip"],
                "Alış Qiyməti": f"{info['baza_qiymet']} AZN",
                "Aylıq Yanacaq": round(monthly_fuel_cost, 2),
                "Aylıq Təmir": round(monthly_repair_cost, 2),
                "Cəmi Aylıq Xərc": round(total_monthly_cost, 2),
                "Sərfəlilik İndeksi": round(score, 1)
            })
            
    if results:
        res_df = pd.DataFrame(results)
        # Sərfəlilik indeksinə görə ən yaxşıları sırala
        res_df = res_df.sort_values(by="Sərfəlilik İndeksi", ascending=False)
        
        st.success("💡 Sizin üçün ən optimal avtomobillərin maliyyə reytinqi:")
        st.dataframe(res_df.set_index("Avtomobil"))
        
        # Qrafik Vizuallaşdırma
        st.subheader("📈 Aylıq Xərclərin Struktur Müqayisəsi")
        fig, ax = plt.subplots(figsize=(10, 4.5))
        
        cars = res_df["Avtomobil"].tolist()
        fuel_costs = res_df["Aylıq Yanacaq"].tolist()
        repair_costs = res_df["Aylıq Təmir"].tolist()
        
        ax.bar(cars, fuel_costs, label="Aylıq Yanacaq Xərci (AZN)", color="royalblue")
        ax.bar(cars, repair_costs, bottom=fuel_costs, label="Gözlənilən Usta Xərci (AZN)", color="orange")
        
        ax.axhline(y=monthly_max_maintenance, color="red", linestyle="--", label="Sizin Maksimum Limitiniz")
        ax.set_ylabel("Aylıq Xərc (AZN)")
        plt.xticks(rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        st.pyplot(fig)
    else:
        st.warning("Təbrik edirik, daxil etdiyiniz büdcə limitlərinə uyğun maşın tapılmadı. Zəhmət olmasa parametrləri genişləndirin.")
        