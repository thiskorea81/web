from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# OpenAI API 키를 환경변수에서 가져옵니다.
openai.api_key = os.getenv('OPENAI_API_KEY')

# Assistant를 생성합니다.
assistant = openai.Assistant.create(
    model="gpt-3.5-turbo",  # 사용할 모델을 지정합니다.
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],  # 필요한 도구를 지정합니다.
)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_message = data['message']

    # 새로운 대화를 위한 Thread를 생성합니다.
    thread = openai.Thread.create()

    # 사용자의 메시지를 Thread에 추가합니다.
    message = openai.Message.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    try:
        # Assistant를 실행합니다.
        run = openai.Run.create(
            assistant_id=assistant.id,
            thread_id=thread.id
        )

        # Assistant의 응답을 받아옵니다.
        run = openai.Run.retrieve(
            assistant_id=assistant.id,
            thread_id=thread.id,
            run_id=run.id
        )

        # Assistant의 응답을 확인합니다.
        messages = openai.Message.list(
            thread_id=thread.id
        )

        # 사용자에게 보낼 메시지를 결정합니다.
        if messages.data:
            response_content = messages.data[-1]['content']['text']['value']
            return jsonify({'response': response_content}), 200
        else:
            return jsonify({'error': 'No response from the assistant.'}), 400
    except Exception as e:
        # 로그에 에러를 출력합니다.
        app.logger.error(f'An error occurred: {str(e)}')
        return jsonify({'error': 'An internal error occurred.'}), 500

@app.route('/')
def index():
    return app.send_static_file('chat.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
