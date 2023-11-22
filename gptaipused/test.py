from flask import Flask, request, redirect, url_for, render_template
import openai
import sqlite3 as sq
import pandas as pd
import env

openai.api_key=env.API_KEY

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/solve')
def show_solve():
    return render_template('index_error.html')

@app.route('/ask')
def show_ask():
    return render_template('index_chatbot.html')

@app.route("/post", methods=['POST'])
def post():
    value = request.form['input']
    stuNum = request.form['stunum']
    stuName = request.form['stuname']

    접두_키워드 = ''
    접미_키워드 = ''
    messages = []
    user_content = 접두_키워드 + value + 접미_키워드

    messages.append({"role": "user", "content": f"{user_content}"})


    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {
            "role": "user",
            "content": user_content,
        },
        ],
    )
    assistant_content= completion.choices[0].message.content

    #db호출
    conn, c = create_connection()

    c.execute("insert into stuQuestions(stuNum, stuName, stuAsk, chatbotAnswer) values(?,?,?,?)",(stuNum, stuName, value, assistant_content))
    c.fetchall()

    conn.commit()

    # 다 사용한 커서 객체를 종료할 때
    c.close()

    # 연결 리소스를 종료할 때
    conn.close()

    return f'''<pre>답변은 다음과 같습니다. {assistant_content}</pre>
    <h1>답변에 대해 만족하셨나요?</h1>
    <form action="/submit" method="post">
        <label for="answer_o">O</label>
        <input type="radio" id="answer_o" name="answer" value="O" required>
        
        <label for="answer_x">X</label>
        <input type="radio" id="answer_x" name="answer" value="X" required>
        <input type="hidden" id="text_input" name="stuNum" value={stuNum}> <br><br>
        <input type="submit" value="제출">
    </form>
    '''


@app.route('/submit', methods=['POST'])
def submit():
    #db호출
    conn, c = create_connection()


    answer = request.form.get('answer')  # HTML 폼에서 'answer' 파라미터 가져오기
    stuNum = request.form.get('stuNum')  # HTML 폼에서 'stuNum' 파라미터 가져오기

    # 데이터베이스에서 가장 마지막으로 stuNum과 일치하는 행을 찾기
    c.execute('SELECT id FROM stuQuestions WHERE stuNum = ? ORDER BY id DESC LIMIT 1', (stuNum,))
    row = c.fetchone()

    if row:
        # 마지막 행의 answer 열에 내용 추가
        c.execute('UPDATE stuQuestions SET answer = ? WHERE id = ?', (answer, row[0]))
        conn.commit()


    # 다 사용한 커서 객체를 종료할 때
    c.close()

    # 연결 리소스를 종료할 때
    conn.close()

    return redirect(url_for('index'))

def get_dataframe_from_db():
    #db호출
    conn, c = create_connection()
    query = "SELECT stuNum, stuName, stuAsk, chatbotAnswer, answer FROM stuQuestions"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@app.route('/db')
def show_db():
    df = get_dataframe_from_db()
    print(df)
    df.to_csv('./result/question.csv', encoding='cp949')
    return render_template('show_db.html', table=df.to_html(classes='table table-striped'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)