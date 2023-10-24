from distutils.log import debug
from fileinput import filename
import pathlib

from flask import *  
app = Flask(__name__)  
  
@app.route('/')  
def main():  
    return '''
<html>  
<head>  
    <title>upload the file : GFG</title>  
</head>  
<body>  
    <form action = "/success" method = "post" enctype="multipart/form-data">  
        <input type="file" name="file" />  
        <input type = "submit" value="Upload">  
    </form>  
</body>  
</html>'''
  
@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        ext = (pathlib.Path(f.filename).suffix)
        id='123'
        f.save('./static/FileStorage/'+id+ext)  
        return "File uploaded successfully"
if __name__ == '__main__':  
    app.run(debug=True)