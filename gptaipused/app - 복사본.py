from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import openai
import os
import sqlite3 as sq
import pandas as pd
#import env

app = Flask(__name__)

# OpenAI API 키를 환경변수에서 가져옵니다.
# 환경변수에 'OPENAI_API_KEY'로 저장되어 있어야 합니다.
openai.api_key = os.getenv('OPENAI_API_KEY')
# openai.api_key=env.API_KEY

#LOCAL DB 연결
def create_connection():
    conn = sq.connect("user_database.db", check_same_thread=False)
    c = conn.cursor()
    return conn, c

#FLASK 실행시 최초 DB생성을 위한 부분
conn, c = create_connection()

c.execute('''create table IF NOT EXISTS stuQuestions(id integer PRIMARY KEY AUTOINCREMENT, 
        stuNum text, stuName text, stuAsk TEXT, chatbotAnswer text, answer text)''')
# 새로운 notices 테이블 생성
c.execute('''CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    date TEXT NOT NULL)''')
print("Table created successfully")
c.close() #커서 종료
conn.close() #커넥션 종료

@app.route('/ask', methods=['POST'])
def ask():
    stuNum = '1111'
    stuName = '홍길동'
    data = request.json
    kor = '한글로 답해주고, '
    ca = '정확한 답은 알려주지 말고 힌트로 제공해줘.'
    messages = []
    user_message = kor+data['message']+ca
    messages.append({"role": "user", "content": f"{user_message}"})
    try:
        response = openai.chat.completions.create(
            model="gpt-4",  # 코드 해석을 위한 모델을 지정하세요.
            messages=[{"role": "user", 
                       "content": user_message,},],
        )

        # 응답에서 코드를 추출하고 형식을 잘 구성합니다.
        code_response = response.choices[0].message.content
        formatted_code = f'Assistant:\n{code_response}\n'  # Markdown 형식으로 코드 블록을 생성합니다.

        #db호출   # 민수쌤 코드
        conn, c = create_connection()

        c.execute("insert into stuQuestions(stuNum, stuName, stuAsk, chatbotAnswer) values(?,?,?,?)",(stuNum, stuName, user_message, code_response))
        c.fetchall()

        conn.commit()

        # 다 사용한 커서 객체를 종료할 때
        c.close()

        # 연결 리소스를 종료할 때
        conn.close()

        return jsonify({'response': formatted_code}), 200
    except Exception as e:
        app.logger.error(f'An error occurred: {str(e)}')
        return jsonify({'error': 'An internal error occurred: {str(e)}'}), 500

def get_dataframe_from_db():
    #db호출
    conn, c = create_connection()
    query = "SELECT stuNum, stuName, stuAsk, chatbotAnswer, answer FROM stuQuestions"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Check if the directory exists
if not os.path.exists('./result'):
    # If not, create the directory
    os.makedirs('./result')

@app.route('/db')
def show_db():
    df = get_dataframe_from_db()
    print(df)
    df.to_csv('./result/question.csv', encoding='cp949')
    return render_template('show_db.html', table=df.to_html(classes='table table-striped'))

@app.route('/export')
def export():
    # DataFrame을 생성합니다. 이 부분을 실제 데이터로 채워야 합니다.
    df = get_dataframe_from_db()
    
    # DataFrame을 CSV 파일로 저장합니다.
    df.to_csv('result.csv', encoding='cp949')
    
    # CSV 파일을 사용자에게 전송합니다.
    return send_file('result.csv',
                     mimetype='text/csv',
                     attachment_filename='result.csv',
                     as_attachment=True)

# 공지사항 데이터베이스 관련
# 1. Create (생성) 
@app.route('/add', methods=['GET', 'POST'])
def add_notice():
    if request.method == 'POST':
        conn, c = create_connection()

        title = request.form['title']
        content = request.form['content']
        #현재 날짜와 시간 설정
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        now = formatted_time  

        c.execute("INSERT INTO notices (title, content, date) VALUES (?, ?, ?)", 
                  (title, content, now))
        conn.commit()

        c.close()
        conn.close()

        df = get_dataframe_from_notice_db()
        print(df)

        return render_template('admin.html', table=df.to_html(classes='table table-striped'))
    else:
        # GET 요청 처리
        return render_template('add_notice.html')

# 2. Read (조회)
@app.route('/notices')
def show_notices():
    conn, c = create_connection()
    c.execute("SELECT * FROM notices")
    notices = c.fetchall()
    c.close()
    conn.close()

    # 이후에는 'notices' 변수를 사용하여 템플릿에 데이터를 전달합니다.
    return render_template('notices.html', notices=notices)

# 3. Update (수정)
@app.route('/update/<int:id>', methods=['POST'])
def update_notice(id):
    conn, c = create_connection()

    title = request.form['title']
    content = request.form['content']

    c.execute("UPDATE notices SET title = ?, content = ? WHERE id = ?", 
              (title, content, id))
    conn.commit()

    c.close()
    conn.close()

    df = get_dataframe_from_notice_db()
    print(df)

    return render_template('admin.html', table=df.to_html(classes='table table-striped'))
# 4. Delete(삭제)
@app.route('/delete', methods=['POST'])
def delete_notice():
    notice_id = request.form.get('noticeId')
    if notice_id:
        conn, c = create_connection()

        c.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
        conn.commit()

        c.close()
        conn.close()

        df = get_dataframe_from_notice_db()
        print(df)

        return render_template('admin.html', table=df.to_html(classes='table table-striped'))
    else:
        return "There is no deleted notice"

@app.route("/")
def index():
    return render_template('index.html')

def get_dataframe_from_notice_db():
    #db호출
    conn, c = create_connection()
    query = "SELECT * FROM notices"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@app.route("/main")
def main():
    df = get_dataframe_from_notice_db()
    print(df)

    return render_template('main.html', table=df.to_html(classes='table table-striped'))

@app.route("/admin")
def admin():
    df = get_dataframe_from_notice_db()
    print(df)

    return render_template('admin.html', table=df.to_html(classes='table table-striped'))

@app.route('/nav1')
def nav1():
    return render_template('nav1.html')

@app.route('/nav2')
def nav2():
    return render_template('nav2.html')

@app.route('/nav3')
def nav3():
    return render_template('nav3.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)