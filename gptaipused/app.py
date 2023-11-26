from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
from openai import OpenAI
import os
import sqlite3 as sq
import pandas as pd

app = Flask(__name__)

# OpenAI API 키를 환경변수에서 가져옵니다.
# 환경변수에 'OPENAI_API_KEY'로 저장되어 있어야 합니다.
client1 = OpenAI()      # 코드 해석
client2 = OpenAI()      # 수학 문제 풀이

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

@app.route('/ask_code', methods=['POST'])
def ask_code():
    stuNum = '1111'
    stuName = '홍길동'
    data = request.json
    kor = '한글로 답해주고, '
    ca = '정확한 답은 알려주지 말고 힌트로 제공해줘.'
    messages = []
    user_message = kor+data['message']+ca

    assistant = client1.beta.assistants.create(
        name = "Code Interpreter",
        model="gpt-3.5-turbo",  # 사용할 모델을 지정합니다.
        instructions="You are a personal code interpreter. Write and run code to answer python questions.",
        tools=[{"type": "code_interpreter"}],  # 필요한 도구를 지정합니다.
    )
    
    # 새로운 대화를 위한 Thread를 생성합니다.
    thread = client1.beta.threads.create()

    # 사용자의 메시지를 Thread에 추가합니다.
    message = client1.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    try:
        # Assistant를 실행합니다.
        run = client1.beta.threads.runs.create(
            assistant_id=assistant.id,
            thread_id=thread.id,
        )

        # Assistant의 응답을 받아옵니다.
        while True:
            if run.status == "completed":
                break
            run = client1.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Assistant의 응답을 확인합니다.
        messages = client1.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # 사용자에게 보낼 메시지를 결정합니다.
        if messages.data:
            # value 값을 저장할 변수
            response_content = ""

            # messages.data의 각 ThreadMessage 객체에 대해 반복
            for message in messages.data:
                # 각 메시지의 content 속성에 대해 반복
                for content in message.content:
                    if content.type == 'text':
                        # 'text' 유형의 content에서 'value' 값을 추출하여 저장
                        response_content = content.text.value
                        break  # 첫 번째 'text' 유형의 content를 찾으면 반복 중단
                if response_content:
                    break  # 'value' 값을 찾으면 바깥쪽 반복도 중단
            
            # 응답에서 코드를 추출하고 형식을 잘 구성합니다.
            code_response = response_content
            formatted_code = f'Assistant:\n{code_response}\n'  # Markdown 형식으로 코드 블록을 생성합니다.
            #db호출   # 민수쌤 코드
            conn, c = create_connection()
            c.execute("insert into stuQuestions(stuNum, stuName, stuAsk, chatbotAnswer) values(?,?,?,?)",
                  (stuNum, stuName, user_message, code_response))
            c.fetchall()
            conn.commit()
            # 다 사용한 커서 객체를 종료할 때
            c.close()
            # 연결 리소스를 종료할 때
            conn.close()

            return jsonify({'response': response_content}), 200

    except Exception as e:
        # 로그에 에러를 출력합니다.
        app.logger.error(f'An error occurred: {str(e)}')
        return jsonify({'error': 'An internal error occurred.'}), 500

@app.route('/ask_math', methods=['POST'])
def ask_math():
    stuNum = '1111'
    stuName = '홍길동'
    data = request.json
    kor = '한글로 답해주고, '
    # ca = '정확한 답은 알려주지 말고 힌트로 제공해줘.'
    messages = []
    user_message = kor+data['message']

    assistant = client2.beta.assistants.create(
        name = "Code Interpreter",
        model="gpt-3.5-turbo",  # 사용할 모델을 지정합니다.
        instructions="You are a personal math tutor. Write and run code to answer math questions.",
        tools=[{"type": "code_interpreter"}],  # 필요한 도구를 지정합니다.
    )
    
    # 새로운 대화를 위한 Thread를 생성합니다.
    thread = client2.beta.threads.create()

    # 사용자의 메시지를 Thread에 추가합니다.
    message = client2.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    try:
        # Assistant를 실행합니다.
        run = client2.beta.threads.runs.create(
            assistant_id=assistant.id,
            thread_id=thread.id,
        )

        # Assistant의 응답을 받아옵니다.
        while True:
            if run.status == "completed":
                break
            run = client2.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Assistant의 응답을 확인합니다.
        messages = client2.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # 사용자에게 보낼 메시지를 결정합니다.
        if messages.data:
            # value 값을 저장할 변수
            response_content = ""

            # messages.data의 각 ThreadMessage 객체에 대해 반복
            for message in messages.data:
                # 각 메시지의 content 속성에 대해 반복
                for content in message.content:
                    if content.type == 'text':
                        # 'text' 유형의 content에서 'value' 값을 추출하여 저장
                        response_content = content.text.value
                        break  # 첫 번째 'text' 유형의 content를 찾으면 반복 중단
                if response_content:
                    break  # 'value' 값을 찾으면 바깥쪽 반복도 중단
            
            # 응답에서 코드를 추출하고 형식을 잘 구성합니다.
            code_response = response_content
            formatted_code = f'Assistant:\n{code_response}\n'  # Markdown 형식으로 코드 블록을 생성합니다.
            #db호출   # 민수쌤 코드
            conn, c = create_connection()
            c.execute("insert into stuQuestions(stuNum, stuName, stuAsk, chatbotAnswer) values(?,?,?,?)",
                  (stuNum, stuName, user_message, code_response))
            c.fetchall()
            conn.commit()
            # 다 사용한 커서 객체를 종료할 때
            c.close()
            # 연결 리소스를 종료할 때
            conn.close()

            return jsonify({'response': response_content}), 200

    except Exception as e:
        # 로그에 에러를 출력합니다.
        app.logger.error(f'An error occurred: {str(e)}')
        return jsonify({'error': 'An internal error occurred.'}), 500

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