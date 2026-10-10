import streamlit as st
import sqlite3
import random

#  Options UI 
st.set_page_config(page_title="AlgoMaster", page_icon="🧠", layout="centered")

#  Complexity 
COMPLEXITIES = ["O(1)", "O(log n)" , "O(log(n * k))", "O(n)", "O(n + k)" ,"O(n log n)", "O(n log m)" , "O(n * k)", "O(n^2)", "O(2^n)", "O(n!)"]

# Database
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
    
    # Delete old good and bad 
    c.execute("DELETE FROM good_solutions WHERE title=?", (title,))
    c.execute("DELETE FROM bad_solutions WHERE title=?", (title,))
    
    # Place cars in new section depend on answer
    if is_correct:
        c.execute("INSERT INTO good_solutions (title, code, time_complexity, space_complexity) VALUES (?, ?, ?, ?)", (title, code, t, s))
    else:
        c.execute("INSERT INTO bad_solutions (title, code, time_complexity, space_complexity, notes) VALUES (?, ?, ?, ?, ?)", (title, code, t, s, notes))
    
    conn.commit()
    conn.close()

# init
init_db()

#   navigation  
st.sidebar.title("Main")
page = st.sidebar.radio("Section: ", ["🎮 Training", "➕ Add card"])

#   add problem  
if page == "➕ Add card":
    st.header("Add into base")
    new_title = st.text_input("Name of problem")
    new_code = st.text_area("Solution: ", height=200)
    col1, col2 = st.columns(2)
    new_t = col1.selectbox("Time Complexity", COMPLEXITIES)
    new_s = col2.selectbox("Space Complexity", COMPLEXITIES)
    
    if st.button("Save", use_container_width=True):
        if new_title and new_code:
            conn = get_db()
            c = conn.cursor()
            # add to all_solutions
            c.execute("INSERT INTO all_solutions (title, code, time_complexity, space_complexity) VALUES (?, ?, ?, ?)", 
                      (new_title, new_code, new_t, new_s))
            conn.commit()
            conn.close()
            st.success(f"Problem '{new_title}' was added!")
        else:
            st.error("Error write title and code!")

#   trainer  
elif page == "🎮 Training":
    st.title("🎯 Algo")
    
    # Regimes
    mode = st.radio("Choose Regime:", 
                    ["🎲 Mix (All problems)", "✅ Right solved problems", "❌ False solved problems"], 
                    horizontal=True)
    
    table_map = {
        "🎲 Mix (All problems)": "all_solutions",
        "✅ Right solved problems": "good_solutions",
        "❌ False solved problems": "bad_solutions"
    }

    # start button
    if st.button("🚀 Give me a problem!", type="primary", use_container_width=True):
        conn = get_db()
        c = conn.cursor()
        c.execute(f"SELECT title, code, time_complexity, space_complexity FROM {table_map[mode]} ORDER BY RANDOM() LIMIT 1")
        problem = c.fetchone()
        conn.close()

        if problem:
            st.session_state['current_problem'] = problem
            st.session_state['answered'] = False
        else:
            st.warning("There is no problems here, choose different regime or add a problem!")

    st.divider()

    
    if 'current_problem' in st.session_state and st.session_state['current_problem']:
        title, code, correct_t, correct_s = st.session_state['current_problem']
        
        st.subheader(f"📝 Problem: {title}")
        st.code(code, language='python') 
    
        col1, col2 = st.columns(2)
        guess_t = col1.selectbox("⏳ Answer: Time Complexity", ["Choose..."] + COMPLEXITIES)
        guess_s = col2.selectbox("💾 Answer: Space Complexity", ["Choose..."] + COMPLEXITIES)
        
        notes = st.text_input("Notions:", placeholder="why failed")

        if st.button("✅ Answer", use_container_width=True):
            if guess_t == "Choose..." or guess_s == "Choose...":
                st.error("choose both time and space")
            else:
                is_correct = (guess_t == correct_t and guess_s == correct_s)
                
                move_solution(title, code, correct_t, correct_s, is_correct, notes)
                
                if is_correct:
                    st.success("🎉 Was added to good")
                else:
                    st.error(f"❌ False: Time {correct_t}, Space {correct_s}. added to Bad.")
                
                st.session_state['current_problem'] = None