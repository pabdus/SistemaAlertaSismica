from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
from datetime import datetime, timedelta
import requests
import csv

account_sid = 'AC7b251f302c1219ff41ce9cfecf982895'
auth_token = 'c03648c464c3ab1abc71d5c15764681e'
twilio_whatsapp_number = 'whatsapp:+14155238886'
twilio_sms_number = '+12056228055'  
recipient_phone_number = '+573229418057'
recipient_whatsapp_number = 'whatsapp:+573229418057'

app = Flask(__name__)

def get_latest_earthquake_data():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    url = f"https://ultimosismo.igp.gob.pe/datos-sismicos-xls/{start_time.strftime('%d-%m-%Y')}/{end_time.strftime('%d-%m-%Y')}/-25.701/-1.396/-87.382/-65.624/2/1/9/0/900"
    response = requests.get(url)
    if response.ok:
        df = pd.read_excel(response.content)
        df['fecha UTC'] = pd.to_datetime(df['fecha UTC'] + ' ' + df['hora UTC'])

        
        df_sorted = df.sort_values('fecha UTC', ascending=False)

    
    return df_sorted


def send_whatsapp(message_body):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=twilio_whatsapp_number,
        to=recipient_whatsapp_number
    )
    return message.sid

def send_sms(message_body):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=twilio_sms_number,
        to=recipient_phone_number
    )
    return message.sid


def store_response(response):
    with open('responses.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.utcnow(), response])


@app.route('/sms', methods=['POST'])
def sms():
    response_body = request.form['Body']
    store_response(response_body.lower())  

if __name__ == '__main__':
    latest_earthquake_data = get_latest_earthquake_data()

    if latest_earthquake_data is not None and not latest_earthquake_data.empty:
      
        latest_earthquake = latest_earthquake_data.iloc[0]

       
        fecha_utc = latest_earthquake['fecha UTC']
        latitud = latest_earthquake['latitud (º)']
        longitud = latest_earthquake['longitud (º)']
        profundidad = latest_earthquake['profundidad (km)']
        magnitud = latest_earthquake['magnitud (M)']

        
        message_body = f"Último sismo en Perú:\nFecha UTC: {fecha_utc} \nLatitud: {latitud}º\nLongitud: {longitud}º\nProfundidad: {profundidad} km\nMagnitud: {magnitud}"

       
        whatsapp_message_id = send_whatsapp(message_body)
        sms_message_id = send_sms(message_body)

        print("WhatsApp enviado correctamente. ID del mensaje:", whatsapp_message_id)
        print("SMS enviado correctamente. ID del mensaje:", sms_message_id)
    else:
        print("No se pudo obtener la información del último sismo en Perú.")

    
    app.run(debug=True)
