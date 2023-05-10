import requests


def send_to_telegram(message):

    apiToken = '5806073657:AAGGz4AnYqATtzPeXTGY_KYQWTBaVhXdV74'
    chatID = '1562103759'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)


send_to_telegram("Hello from Python!")
