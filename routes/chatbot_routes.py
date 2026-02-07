from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message', '').strip().lower()

    if not user_message:
        return jsonify({'response': 'Please say something!'})

    # Simple keyword-based logic
    response = ""
    
    if any(word in user_message for word in ['hello', 'hi', 'hey', 'greetings']):
        response = "Hello! I am the University AI Assistant. How can I help you today?"
    elif any(word in user_message for word in ['enroll', 'register', 'admission', 'join', 'sign up']):
        response = "To enroll, please click on the 'Register' button in the top right corner. You'll need to provide your personal details and previous academic records."
    elif any(word in user_message for word in ['fee', 'payment', 'cost', 'price', 'amount', 'paid']):
        response = "We offer various payment methods including UPI and Bank Transfer. You can view detailed fee structures in the 'Courses' section."
    elif any(word in user_message for word in ['course', 'subject', 'program', 'degree', 'syllabus']):
        response = "We offer a variety of courses including MCA, MBA, and BCA. Navigate to the 'Courses' page to see the full catalog and details."
    elif any(word in user_message for word in ['contact', 'help', 'support', 'phone', 'email', 'number', 'address']):
        response = "You can reach our administrative support at admin@university.com or call us at +91-1234567890."
    elif 'thank' in user_message:
        response = "You're welcome! Let me know if you have any other questions."
    elif any(word in user_message for word in ['bye', 'goodbye', 'see you']):
        response = "Goodbye! Have a great day!"
    else:
        response = "I'm sorry, I didn't quite understand that. You can ask me about enrollment, fees, courses, or contact information."

    return jsonify({'response': response})
