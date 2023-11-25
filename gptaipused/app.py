from flask import Flask, request, jsonify, render_template, send_file
import openai
import os
import sqlite3 as sq
import pandas as pd
import env

app = Flask(__name__)

# OpenAI API 키를 환경변수에서 가져옵니다.
# 환경변수에 'OPENAI_API_KEY'로 저장되어 있어야 합니다.
# openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_key=env.API_KEY

#LOCAL DB 연결
def create_connection():
    conn = sq.connect("user_database.db", check_same_thread=False)
    c = conn.cursor()
    return conn, c

#FLASK 실행시 최초 DB생성을 위한 부분
conn, c = create_connection()

c.execute('''create table IF NOT EXISTS stuQuestions(id integer PRIMARY KEY AUTOINCREMENT, 
        stuNum text, stuName text, stuAsk TEXT, chatbotAnswer text, answer text)''')
c.close() #커서 종료
conn.close() #커넥션 종료

@app.route('/ask', methods=['POST'])
def ask():
    stuNum = '1111'
    stuName = '홍길동'
    data = request.json
    kor = '한글로 답해주고, '
    ca = '정확한 답은 알려주지 말고 힌트로 제공해줘.'
    user_message = kor+data['message']+ca
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 코드 해석을 위한 모델을 지정하세요.
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": user_message}]
        )

        # 응답에서 코드를 추출하고 형식을 잘 구성합니다.
        code_response = response.choices[0].message['content']
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

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/info')
def info():
    return render_template('01info.html')

@app.route('/ai')
def ai():
    return render_template('02ai.html')

@app.route('/exercise')
def exercise():
    return render_template('03exer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)