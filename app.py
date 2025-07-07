from flask import Flask, request, send_file, render_template, after_this_request
import os
import pdfkit
import mammoth
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads' #yaha ek folder create horaha hai uploads naam ka jaha files upload honge .docx waale
if not os.path.exists(UPLOAD_FOLDER): #yaha check horaha hai ki uploads naam ka folder exist karta hai ya nahi
    os.makedirs(UPLOAD_FOLDER) #agar nhi karta toh ye fir folder create kardega


WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" #ye ek engine hai joh html ko pdf mein convert karega, isska path hum ek variable main store
#karahe hai aur usko pdfkit mein configuration ke liye use karahe hai 
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

@app.route('/')
def index():
    return render_template('homepage.html') #homepage display ke liye approute

@app.route('/convert', methods=['POST']) #yaha pe input leke conversion horaha hai
def convert():
    
    file = request.files['file'] #input liya file ka frontend se aur file naam ke variable main store kardiya
    
    if not file or file.filename == '': #agar file upload nahi ki yaa nameless file hai toh error aayega 
        return "No file selected", 400

    if not file.filename.endswith('.docx'):
        return "Only .docx files are allowed", 400

    safe_filename = secure_filename(file.filename) #ye filename jaise agar filename tera hello@123 hai ussko ye hello123 kardega special char hata dega 
    input_path = os.path.join(UPLOAD_FOLDER, safe_filename) #idhar aapna safefilename store horaha hai uploads folder ke andar
    output_pdf_name = safe_filename.replace('.docx', '.pdf') #ye format change karaha hai .docx se .pdf main
    output_path = os.path.join(UPLOAD_FOLDER, output_pdf_name) #idhar output path ban raha hai jaha pdf file store hogi


    file.save(input_path) #ye file ko uploads folder main save karaha hai

    try:
       #sabse phehele try karenge if convert hoga ki nahi agar hoga toh try block run hoga agar nahi toh except block run hoga
       #toh fir yaha pe hum mammoth library use karahe hai joh docx file ko html main convert kardega
        with open(input_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value 

      #yaha pe joh html bana hai ussko pdfkit use karke pdf main convert karenge
        pdfkit.from_string(html_content, output_path, configuration=config)

        #fir convert ke baad frontend ko response bhej denge output pdf file ke saath using send_file method

        response = send_file(
            output_path,
            as_attachment=True,
            download_name=output_pdf_name,
            mimetype='application/pdf'
        )

       #jaise hi tera file download hoga uske baad cleanup function run hoga joh input aur output file ko delete kar dega waarna overlap hoga error dega
        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                print("Cleanup error:", e)
            return response

        return response

    except Exception as e:
        return f"Conversion failed: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
