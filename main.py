from dotenv import load_dotenv
import os

from flask import Flask, render_template, request, jsonify
import json
import requests
import hmac

load_dotenv()

GEETEST_ID = os.getenv("GEETEST_ID")
GEETEST_KEY = os.getenv("GEETEST_KEY")

app = Flask(__name__)

# Use Geetest
api_server = 'http://gcaptcha4.geetest.com'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rain/join', methods=['POST'])
def validate():

    print("VOU VALIDAR")

    result = request.get_json()
    print("Resultado do frontend: ")
    print(result)

    lot_number = result.get('lot_number')
    captcha_output = result.get('captcha_output')
    pass_token = result.get('pass_token')
    gen_time = result.get('gen_time')

    captcha_id = result.get('captcha_id')

    # 3. Generate signature
    # Using standard hmac algorithms to generate signatures, using the user's current verification serial number lot_number as the original message, and the client's verification private key as the key
    # Using sha256 hash algorithm to hash message and key in one direction to generate the final signature
    lotnumber_bytes = lot_number.encode()
    prikey_bytes = GEETEST_KEY.encode()
    sign_token = hmac.new(prikey_bytes, lotnumber_bytes, digestmod='SHA256').hexdigest()

    # 4. Upload verification parameters to the second verification interface of GeeTest to verify the user verification status
    query = {
        "lot_number": lot_number,
        "captcha_output": captcha_output,
        "pass_token": pass_token,
        "gen_time": gen_time,
        "sign_token": sign_token,
    }

    url = api_server + '/validate' + '?captcha_id={}'.format(GEETEST_ID)
    print(url)

    try:
        res = requests.post(url, query)

        print("resposta do request ao api_Server:")
        print(res.text)

        if res.status_code == 200:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'fail'}), 400

    except Exception as e:
        gt_msg = {'result': 'success', 'reason': 'request geetest api fail'}

        # 5. According to the user authentication status returned by GeeTest, the website owner conducts his own business logic
        if gt_msg['result'] == 'success':
            print({'login': 'success', 'reason': gt_msg['reason']})
        else:
            print({'login': 'fail', 'reason': gt_msg['reason']})


@app.route('/api/teste', methods=['POST'])
def test_post():
    # Print entire request data
    print(f"Request URL: {request.url}")
    print(f"Request Headers: {dict(request.headers)}")
    print(f"Request Body: {request.get_data().decode('utf-8')}")

    # If the request is JSON, you can decode it
    try:
        json_data = request.get_json()
        print(f"Parsed JSON Data: {json_data}")
    except Exception as e:
        print(f"Failed to parse JSON: {str(e)}")


    # Get the Authorization header
    auth = request.headers.get('Authorization')

    if not auth:
        print("Authorization header is missing")

    print(auth)

    response = {
        "success": True
    }

    #return json.dumps({"status": "Received"}), 200
    return json.dumps(response), 200


if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
