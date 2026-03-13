import streamlit as st
import pandas as pd
import os
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# 1. Настройка страницы (должна быть самой первой командой Streamlit)
st.set_page_config(page_title="Технический аудит 2026", layout="wide", page_icon="🛡️")

# 2. Логотип и призыв (из загруженного вами файла)
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)
else:
    # Если файла еще нет в GitHub, покажем текстовый заголовок
    st.subheader("Ivan Rudoy | IT Audit")

st.markdown("### 📞 **Хотите такой опросник — звоните!**")
st.divider()

st.title("📋 Технический аудит ИТ и ИБ (2026)")

# --- Инициализация данных ---
data = {}
security_points = 0

# --- Блок 1 (на основе вашего документа) ---
st.header("Блок 1: Общая информация")
data['Сотрудников'] = st.number_input("1. Общее количество сотрудников:", min_value=0, step=1)
has_it = st.toggle("2. Есть выделенный ИТ-департамент?")

if has_it:
    col1, col2 = st.columns(2)
    with col1:
        data['АРМ'] = st.number_input("1.1. Количество АРМ:", min_value=0)
        data['Серверы_Физ'] = st.number_input("1.2. Физических серверов:", min_value=0)
    with col2:
        data['Серверы_Вирт'] = st.number_input("1.2. Виртуальных серверов:", min_value=0)
        data['Почта'] = st.selectbox("1.6. Почта:", ["Cloud", "On-Prem"])

# --- Блок ИБ и Скоринг ---
st.header("Блок 3: Информационная Безопасность")
if st.toggle("Внедрены системы защиты?"):
    # Критические системы (дают баллы)
    if st.checkbox("MFA/2FA (Двухфакторная аутентификация)"):
        data['MFA'] = "Да"; security_points += 20
    else: data['MFA'] = "Нет"

    if st.checkbox("NGFW (Межсетевой экран)"):
        data['NGFW'] = "Да"; security_points += 20
    else: data['NGFW'] = "Нет"

    if st.checkbox("Резервное копирование (Backup)"):
        data['Backup'] = "Да"; security_points += 30
    else: data['Backup'] = "Нет"

    if st.checkbox("SIEM (Мониторинг инцидентов)"):
        data['SIEM'] = "Да"; security_points += 30
    else: data['SIEM'] = "Нет"

# --- Функция красивого Excel ---
def create_styled_report(results, score):
    output = BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Аналитика Аудита"

    # Стилизация
    blue_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    white_font = Font(color="FFFFFF", bold=True)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # Шапка отчета
    ws['A1'] = "РЕЗУЛЬТАТЫ ТЕХНИЧЕСКОГО АУДИТА 2026"
    ws['A1'].font = Font(bold=True, size=14)
    ws.merge_cells('A1:C1')

    # Скоринг
    ws['A3'] = "ИНДЕКС ЗРЕЛОСТИ ИБ:"
    ws['B3'] = f"{score} / 100"
    # Цвет балла
    bg_color = "00B050" if score > 70 else "FFCC00" if score > 40 else "FF0000"
    ws['B3'].fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")

    # Данные
    headers = ["Параметр", "Значение", "Анализ риска"]
    for col, text in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=text)
        cell.fill = blue_fill
        cell.font = white_font

    for i, (k, v) in enumerate(results.items(), 6):
        ws.cell(row=i, column=1, value=k).border = border
        ws.cell(row=i, column=2, value=str(v)).border = border
        # Аналитика
        if v == "Нет":
            cell_risk = ws.cell(row=i, column=3, value="ВЫСОКИЙ РИСК")
            cell_risk.font = Font(color="FF0000", bold=True)
        else:
            ws.cell(row=i, column=3, value="Норма")
    
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 20

    wb.save(output)
    return output.getvalue()

# --- Выгрузка ---
st.divider()
if st.button("📊 Сгенерировать экспертный отчет"):
    excel_file = create_styled_report(data, security_points)
    st.success(f"Анализ завершен! Ваш балл: {security_points}")
    st.download_button("📥 Скачать Excel с аналитикой", excel_file, "Audit_Expert_Report.xlsx")
