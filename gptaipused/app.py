from flask import Flask, request, jsonify
import openai
import os
#import env

app = Flask(__name__)

# OpenAI API 키를 환경변수에서 가져옵니다.
# 환경변수에 'OPENAI_API_KEY'로 저장되어 있어야 합니다.
# openai.api_key = env.API_KEY
openai.api_key = os.getenv('OPENAI_API_KEY')
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    try:
        response = openai.Completion.create(
            engine="davinci", 
            prompt=data['message'], 
            max_tokens=150
        )
        return jsonify({'response': response.choices[0].text.strip()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat.html')
def chat():
    return app.send_static_file('chat.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
