from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

from PIL import Image
import pytesseract
import io
from twilio.rest import Client 
import openai
from pydub import AudioSegment

openai.api_key = "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"
app = Flask(__name__)


# @app.route("/wa")
# def wa_hello():
#     return "Hello, World!"



def chatGPT(msg):
    completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": msg}]
            )
    if completion.choices and completion.choices[0].message:
                mytext = completion.choices[0].message.content
    else:
                mytext = "No response from the API"
    print("reply-->",mytext)
    return mytext
      


@app.route("/", methods=['POST'])
def wa_sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    Fetch_msg= request.form
    print("Fetch_msg-->",Fetch_msg)
    txt=''
    try: # Storing the file that user send to the Twilio whatsapp number in our computer
        msg_url=request.form.get('MediaUrl0')  # Getting the URL of the file
        print("msg_url-->",msg_url)
        msg_ext=request.form.get('MediaContentType0')  # Getting the extension for the file
        print("msg_ext-->",msg_ext)
        ext = msg_ext.split('/')[-1]
        print("ext-->",ext)
        if msg_url != None:
            json_path = requests.get(msg_url)
            filename = msg_url.split('/')[-1]
            print(filename)
            open(filename+"."+ext, 'wb').write(json_path.content)  # Storing the file
        
        # path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        response = requests.get(msg_url)
        # print( type(response) ) # <class 'requests.models.Response'>
        img = Image.open(io.BytesIO(response.content))
        # print( type(img) ) # <class 'PIL.JpegImagePlugin.JpegImageFile'>
        # Providing the tesseract
        # executable location to pytesseract library
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
        # Passing the image object to
        # image_to_string() function
        # This function will
        # extract the text from the image
        txt = pytesseract.image_to_string(img)
        # Displaying the extracted text
        print(txt[:-1])
        if msg_url != None:
            json_path = requests.get(msg_url)
            filename = msg_url.split('/')[-1]
            print(filename)
            open(filename+"."+ext, 'wb').write(json_path.content)  # Storing the file
    except:
        print("no url-->>")

    msg = request.form.get('Body').lower()  # Reading the message from the whatsapp
    print("msg-->",msg)
    resp = MessagingResponse()
    reply=resp.message()

    

    # Text response
    if msg_ext == None:
       mytext=chatGPT(msg)
       reply.body(mytext)
    elif msg_ext=='audio/ogg':
        AudioSegment.from_file(filename+"."+ext).export(filename+"."+"mp3", format="mp3")
        file = open(filename+"."+"mp3", "rb")
        transcription = openai.Audio.transcribe("whisper-1", file)
        print("audio text\n",transcription['text'])
        mytext=chatGPT(transcription['text'])
        reply.body(mytext)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)


