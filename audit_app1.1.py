import streamlit.web.cli as stcli
import os, sys, webbrowser, time, base64
from threading import Thread

# ПОЛНЫЙ КОД ОПРОСНИКА С ЛОГОТИПОМ И АНАЛИТИКОЙ
APP_CODE = """
import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

st.set_page_config(page_title="Технический аудит 2026", layout="wide", page_icon="🛡️")

# --- Функция для вставки логотипа (Base64) ---
def get_base64_image(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ПРИМЕЧАНИЕ: Для работы логотипа в EXE он должен лежать в папке при сборке
# Если файла нет, будет просто текст.
try:
    logo_path = "logo.png" # Переименуйте ваше лого в logo.png
    st.image(logo_path, width=200)
except:
    st.subheader("Ivan Rudoy | IT Audit")

st.markdown("### 📞 **Хотите такой опросник — звоните!**")
st.divider()

st.title("📋 Технический аудит ИТ и ИБ (2026)")
data = {}

# Помощники выбора
def get_choice(label, options, key):
    res = st.selectbox(label, options + ["Другое"], key=f"s_{key}")
    return st.text_input(f"Уточните ({label}):", key=f"ot_{key}") if res == "Другое" else res

def get_multi(label, options, key):
    res = st.multiselect(label, options + ["Другое"], key=f"m_{key}")
    if "Другое" in res:
        other = st.text_input(f"Свой вариант ({label}):", key=f"mot_{key}")
        return ", ".join([x for x in res if x != "Другое"] + ([other] if other else []))
    return ", ".join(res)

# --- СБОР ДАННЫХ (Кратко для примера логики) ---
col_main1, col_main2 = st.columns(2)
with col_main1:
    data['Штат'] = st.number_input("Общее количество сотрудников:", min_value=0)
    has_it = st.toggle("Есть ИТ-департамент?", key="it_t")
with col_main2:
    data['АРМ'] = st.number_input("Кол-во АРМ:", min_value=0)
    has_is = st.toggle("Внедрены системы защиты (ИБ)?", key="is_t")

# Блок ИБ (для скоринга)
security_score = 0
if has_is:
    st.subheader("Инструменты защиты")
    if st.checkbox("MFA/2FA (Двухфакторка)"): 
        data['MFA'] = "Да"; security_score += 20
    else: data['MFA'] = "Нет"
    
    if st.checkbox("NGFW (Межсетевой экран нового поколения)"): 
        data['NGFW'] = "Да"; security_score += 20
    else: data['NGFW'] = "Нет"
    
    if st.checkbox("SIEM/SOC (Мониторинг инцидентов)"): 
        data['SIEM'] = "Да"; security_score += 30
    else: data['SIEM'] = "Нет"
    
    if st.checkbox("Резервное копирование (Бэкапы)"): 
        data['Backup'] = "Да"; security_score += 30
    else: data['Backup'] = "Нет"

# --- ЛОГИКА КРАСИВОГО EXCEL ---
def create_styled_excel(data_dict, score):
    out = BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Результат аудита"

    # Стили
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    white_font = Font(color="FFFFFF", bold=True, size=12)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # Заголовок отчета
    ws.merge_cells('A1:C1')
    ws['A1'] = "ОТЧЕТ ПО ТЕХНИЧЕСКОМУ АУДИТУ 2026"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')

    # Скоринг
    ws['A3'] = "ИНДЕКС ЗРЕЛОСТИ ИБ:"
    ws['B3'] = f"{score} / 100"
    color = "FF0000" if score < 40 else "FFCC00" if score < 70 else "00B050"
    ws['B3'].fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    ws['B3'].font = Font(bold=True)

    # Таблица данных
    ws['A5'] = "Параметр"; ws['B5'] = "Значение"; ws['C5'] = "Статус"
    for cell in ['A5', 'B5', 'C5']:
        ws[cell].fill = header_fill
        ws[cell].font = white_font

    row = 6
    for k, v in data_dict.items():
        ws.cell(row=row, column=1, value=k).border = border
        ws.cell(row=row, column=2, value=str(v)).border = border
        # Простая аналитика в колонке C
        if v == "Нет" and k in ['MFA', 'NGFW', 'SIEM', 'Backup']:
            ws.cell(row=row, column=3, value="РИСК").font = Font(color="FF0000", bold=True)
        row += 1

    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 15

    wb.save(out)
    return out.getvalue()

st.divider()
if st.button("📊 Сформировать экспертный отчет"):
    excel_data = create_styled_excel(data, security_score)
    st.success(f"Аналитика завершена. Ваш балл безопасности: {security_score}")
    st.download_button("📥 Скачать экспертный Excel", excel_data, "IT_Audit_Expert_Report.xlsx")
"""

def open_browser():
    time.sleep(5)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    with open("temp_app.py", "w", encoding="utf-8") as f:
        f.write(APP_CODE)
    Thread(target=open_browser).start()
    sys.argv = ["streamlit", "run", "temp_app.py", "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())