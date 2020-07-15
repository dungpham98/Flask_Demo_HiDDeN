from flask import Flask, escape, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os,subprocess,shutil
from actions.process import process
filetype=['.jpg','.pgm','.png','jpeg']
homedir = "/home/tuandung/HiDDeN/HiDDeN-block/Input_img"
PEOPLE_FOLDER = os.path.join('static', 'people_photo')
PEOPLE_FOLDER2 = os.path.join('static', 'people_photo2')
PEOPLE_IN = os.path.join('static', 'people_input')
HiDDeN_BIN="/home/tuandung/HiDDeN/HiDDeN-block/"
HiDDeN_BIN2="/home/tuandung/HiDDeN/Hidden_Mismatch/"
my_env = os.environ.copy()
my_env["PATH"] = "/usr/sbin:/sbin:" + my_env["PATH"]
glob_file = "xxx"

app = Flask(__name__, static_folder='static')


@app.route('/')
def hello():
    return render_template('homepage.html')


@app.route('/process')
def render_process_page():
    return render_template('process.html')


@app.route('/api/processing', methods=['POST'])
def processing():
    try:
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            fhome = os.path.join(homedir,"valid_class", filename)
            shutil.rmtree(os.path.join(homedir,"valid_class"))
            shutil.rmtree(PEOPLE_FOLDER)
            shutil.rmtree(PEOPLE_FOLDER2)
            shutil.rmtree(PEOPLE_IN)
            os.makedirs(PEOPLE_FOLDER)
            os.makedirs(PEOPLE_FOLDER2)
            os.makedirs(PEOPLE_IN)
            os.makedirs(os.path.join(homedir,"valid_class"))
            fname = os.path.join(PEOPLE_FOLDER, filename)#output file
            fname2 = os.path.join(PEOPLE_FOLDER2, filename)#output file

            f_in = os.path.join(PEOPLE_IN, filename)
            glob_file = fname
            file.save(fhome)
            shutil.copyfile(fhome, f_in)
            result = filename[-4:]
            if result not in filetype:
                return jsonify({'error': 'File is invalid, Please insert an image file'})
            else:
                p = subprocess.Popen(["python3",HiDDeN_BIN+"validate-trained-models.py", "-d", HiDDeN_BIN+"HiddenCOCO",
                            "-r",HiDDeN_BIN+"test_0.2_32_def", "-b", "16", "-o",PEOPLE_FOLDER,
                            "-i",homedir])
                p.wait()

                p2 = subprocess.Popen(["python3",HiDDeN_BIN2+"validate-trained-models.py", "-d", HiDDeN_BIN2+"HiddenCOCO",
                            "-r",HiDDeN_BIN2+"test_0.2_mse_2", "-b", "1", "-o",PEOPLE_FOLDER2,
                            "-i",homedir])
                p2.wait()
                #render_template('process.html',res_img = fname)
                return jsonify({'result': filename,'img_out':fname,'img_out2':fname2,'img_in':f_in})
        return jsonify({'error': 'File is required'})
    except:
        return jsonify({'error': 'ERROR'})

if __name__ == '__main__':
    app.run(debug=True)
