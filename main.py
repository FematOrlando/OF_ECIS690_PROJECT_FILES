from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message

import pickle
import numpy as np

app = Flask(__name__)
model = pickle.load(open('nbclassifier.pkl', 'rb'))
scaler = pickle.load(open('scaler.pickle', 'rb'))
#mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.fastmail.com'  # 'smtps-proxy.fastmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'capstonetest690@fastmail.com'
app.config['MAIL_PASSWORD'] = 'vnlxrw6ydnnp369d'
app.config['MAIL_DEFAULT_SENDER'] = 'capstonetest690@fastmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True

mail = Mail(app)

@app.route('/')
def home():
    return render_template('card_list.html')


@app.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''

    data_list = request.form.getlist("Transaction List")
    transactions = data_list[0].split(",")

    float_features = [float(x) for x in transactions]
    pre_final_features = np.array([float_features])

    final_features = scaler.transform(pre_final_features)

    prediction = model.predict(final_features)
    output = "True" if prediction[0] == 1 else "False"

    if output == "True":
        # Prepare email content
        subject = "Potential Fraud Alert!"
        body = f"A potential fraudulent transaction has been detected! User transaction data: {data_list[0]}"
        recipients = ['capstoneecis690@gmail.com']
        

        msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=recipients, body=body)
        try:
            mail.send(msg)
            sent_mail = 'SENT EMAIL'
        except Exception as e:
            sent_mail = f'FAILED TO SEND EMAIL: {e}'

    else:
        sent_mail = 'No Email Sent'

    return render_template(
        'card_list.html',
        prediction_text=f'FRAUD ALERT: {output}',
        user_list=data_list[0],
        scaled_features=final_features.tolist(),  # Convert to list for template rendering
        sent_mail=sent_mail
    )


if __name__ == "__main__":
    app.run(debug=True)
