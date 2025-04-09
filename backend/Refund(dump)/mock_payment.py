from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/refund', methods=['POST'])
def refund():
    data = request.json
    print("Mock Payment Microservice received refund request:", data)
    return jsonify({"message": "Refund processed", "success": True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)