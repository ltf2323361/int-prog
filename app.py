from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/giris')
def giris():
    return render_template('giris.html')

@app.route('/kayit')
def kayit():
    return render_template('kayit.html')

@app.route('/yonetici-giris')
def yonetici_giris():
    return render_template('yonetici_giris.html')

@app.route('/yonetici-kayit')
def yonetici_kayit():
    return render_template('yonetici_kayit.html')

@app.route('/araclar')
def araclar():
    return render_template('araclar.html')

@app.route('/kiralama')
def kiralama():
    return render_template('kiralama.html')

@app.route('/istatistikler')
def istatistikler():
    return render_template('istatistikler.html')

if __name__ == '__main__':
    app.run(debug=True) 