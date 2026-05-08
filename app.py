import streamlit as st
import sqlite3
import random

# --- НАСТРОЙКИ UI ---
st.set_page_config(page_title="AlgoMaster", page_icon="🧠", layout="centered")

# --- СПИСОК СЛОЖНОСТЕЙ ---
COMPLEXITIES = ["O(1)", "O(log n)" , "O(log(n * k))", "O(n)", "O(n + k)" ,"O(n log n)", "O(n log m)" , "O(n * k)", "O(n^2)", "O(2^n)", "O(n!)"]

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def get_db():
    return sqlite3.connect('algo_vault.db', check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    schema = '''
        title TEXT NOT NULL, code TEXT, 
        time_complexity TEXT, space_complexity TEXT, 
        date_solved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    '''
    c.execute(f"CREATE TABLE IF NOT EXISTS all_solutions (id INTEGER PRIMARY KEY AUTOINCREMENT, {schema})")
    c.execute(f"CREATE TABLE IF NOT EXISTS good_solutions (id INTEGER PRIMARY KEY AUTOINCREMENT, {schema})")
    c.execute(f"CREATE TABLE IF NOT EXISTS bad_solutions (id INTEGER PRIMARY KEY AUTOINCREMENT, {schema}, notes TEXT)")
    conn.commit()
    conn.close()

def move_solution(title, code, t, s, is_correct, notes=""):
    conn = get_db()
    c = conn.cursor()
    
    # 1. Удаляем старые записи из Good и Bad, чтобы не было дубликатов
    c.execute("DELETE FROM good_solutions WHERE title=?", (title,))
    c.execute("DELETE FROM bad_solutions WHERE title=?", (title,))
    
    # 2. Помещаем в нужную таблицу в зависимости от ответа
    if is_correct:
        c.execute("INSERT INTO good_solutions (title, code, time_complexity, space_complexity) VALUES (?, ?, ?, ?)", (title, code, t, s))
    else:
        c.execute("INSERT INTO bad_solutions (title, code, time_complexity, space_complexity, notes) VALUES (?, ?, ?, ?, ?)", (title, code, t, s, notes))
    
    conn.commit()
    conn.close()

# Инициализируем базу при старте
init_db()

# --- БОКОВОЕ МЕНЮ (НАВИГАЦИЯ) ---
st.sidebar.title("Меню")
page = st.sidebar.radio("Куда пойдем?", ["🎮 Тренажер", "➕ Добавить задачу"])

# --- СТРАНИЦА: ДОБАВЛЕНИЕ ЗАДАЧИ ---
if page == "➕ Добавить задачу":
    st.header("Добавить новую задачу в базу")
    new_title = st.text_input("Название (например: Two Sum)")
    new_code = st.text_area("Код решения (вставь сюда):", height=200)
    col1, col2 = st.columns(2)
    new_t = col1.selectbox("Time Complexity", COMPLEXITIES)
    new_s = col2.selectbox("Space Complexity", COMPLEXITIES)
    
    if st.button("Сохранить в базу", use_container_width=True):
        if new_title and new_code:
            conn = get_db()
            c = conn.cursor()
            # По умолчанию кидаем в all_solutions
            c.execute("INSERT INTO all_solutions (title, code, time_complexity, space_complexity) VALUES (?, ?, ?, ?)", 
                      (new_title, new_code, new_t, new_s))
            conn.commit()
            conn.close()
            st.success(f"Задача '{new_title}' успешно добавлена!")
        else:
            st.error("Заполни название и код!")

# --- СТРАНИЦА: ТРЕНАЖЕР ---
elif page == "🎮 Тренажер":
    st.title("🎯 Algo Тренажер")
    
    # Выбор режима
    mode = st.radio("Выбери режим тренировки:", 
                    ["🎲 Микс (Все задачи)", "✅ Только решенные правильно", "❌ Работа над ошибками"], 
                    horizontal=True)
    
    table_map = {
        "🎲 Микс (Все задачи)": "all_solutions",
        "✅ Только решенные правильно": "good_solutions",
        "❌ Работа над ошибками": "bad_solutions"
    }

    # Кнопка старта
    if st.button("🚀 Дать задачу!", type="primary", use_container_width=True):
        conn = get_db()
        c = conn.cursor()
        c.execute(f"SELECT title, code, time_complexity, space_complexity FROM {table_map[mode]} ORDER BY RANDOM() LIMIT 1")
        problem = c.fetchone()
        conn.close()

        if problem:
            st.session_state['current_problem'] = problem
            st.session_state['answered'] = False
        else:
            st.warning("В этой категории пока пусто! Выбери другой режим или добавь задачи.")

    st.divider()

    # Если задача выбрана, показываем интерфейс игры
    if 'current_problem' in st.session_state and st.session_state['current_problem']:
        title, code, correct_t, correct_s = st.session_state['current_problem']
        
        st.subheader(f"📝 Задача: {title}")
        st.code(code, language='python') # Красивая подсветка кода!
        
        # Инпуты для ответов
        col1, col2 = st.columns(2)
        guess_t = col1.selectbox("⏳ Твой ответ: Time Complexity", ["Выбери..."] + COMPLEXITIES)
        guess_s = col2.selectbox("💾 Твой ответ: Space Complexity", ["Выбери..."] + COMPLEXITIES)
        
        notes = st.text_input("Заметки (по желанию):", placeholder="Если ошибешься, запиши сюда почему...")

        # Проверка
        if st.button("✅ Ответить", use_container_width=True):
            if guess_t == "Выбери..." or guess_s == "Выбери...":
                st.error("Пожалуйста, выбери оба варианта сложности!")
            else:
                is_correct = (guess_t == correct_t and guess_s == correct_s)
                
                # Двигаем задачу по таблицам
                move_solution(title, code, correct_t, correct_s, is_correct, notes)
                
                if is_correct:
                    st.success("🎉 ВЕРНО! Задача помечена как усвоенная (перемещена в Good).")
                else:
                    st.error(f"❌ ОШИБКА! Правильно: Time {correct_t}, Space {correct_s}. Отправлено в Bad.")
                
                # Убираем задачу с экрана, чтобы можно было нажать "Дать задачу" снова
                st.session_state['current_problem'] = None