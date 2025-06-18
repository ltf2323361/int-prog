from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///araclar.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "cokgizlisifre"
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    sifre = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(10), nullable=False)  # 'admin' veya 'musteri'

class Arac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marka = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    fiyat = db.Column(db.Integer, nullable=False)
    kirada = db.Column(db.Boolean, default=False)
    resim_url = db.Column(db.String(200), nullable=True)

class Kiralama(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    arac_id = db.Column(db.Integer, db.ForeignKey('arac.id', ondelete='CASCADE'), nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    bitis_tarihi = db.Column(db.DateTime, nullable=True)
    tutar = db.Column(db.Integer, nullable=False)
    gun_sayisi = db.Column(db.Integer, nullable=False, default=1)
    iptal_edildi = db.Column(db.Boolean, default=False)
    durum = db.Column(db.String(20), default='beklemede')  # beklemede, onaylandı, reddedildi
    user = db.relationship('User', backref=db.backref('kiralamalar', cascade='all, delete-orphan'))
    arac = db.relationship('Arac', backref=db.backref('kiralamalar', cascade='all, delete-orphan'))

class Yorum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    arac_id = db.Column(db.Integer, db.ForeignKey('arac.id', ondelete='CASCADE'), nullable=False)
    puan = db.Column(db.Integer, nullable=False)
    yorum = db.Column(db.Text, nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('yorumlar', cascade='all, delete-orphan'))
    arac = db.relationship('Arac', backref=db.backref('yorumlar', cascade='all, delete-orphan'))

class Favori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    arac_id = db.Column(db.Integer, db.ForeignKey('arac.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('favoriler', cascade='all, delete-orphan'))
    arac = db.relationship('Arac', backref=db.backref('favori_kullanicilar', cascade='all, delete-orphan'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        isim = request.form["isim"]
        email = request.form["email"]
        sifre = request.form["sifre"]
        rol = request.form.get("rol", "musteri")
        if User.query.filter_by(email=email).first():
            flash("Bu email zaten kayıtlı.", "danger")
            return redirect(url_for("register"))
        yeni_kullanici = User(
            isim=isim,
            email=email,
            sifre=generate_password_hash(sifre),
            rol=rol
        )
        db.session.add(yeni_kullanici)
        db.session.commit()
        flash("Kayıt başarılı, giriş yapabilirsiniz.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        sifre = request.form["sifre"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.sifre, sifre):
            login_user(user)
            flash("Giriş başarılı!", "success")
            if user.rol == "admin":
                return redirect(url_for("admin_panel"))
            else:
                return redirect(url_for("panel"))
        else:
            flash("Hatalı email veya şifre.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Çıkış yapıldı.", "info")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    araclar = Arac.query.all()
    return render_template("index.html", araclar=araclar)

@app.route("/arac/<int:arac_id>", methods=["GET", "POST"])
@login_required
def arac_detay(arac_id):
    arac = Arac.query.get_or_404(arac_id)
    yorumlar = Yorum.query.filter_by(arac_id=arac_id).order_by(Yorum.tarih.desc()).all()
    ort_puan = None
    if yorumlar:
        ort_puan = round(sum([y.puan for y in yorumlar]) / len(yorumlar), 1)
    kiralama = Kiralama.query.filter_by(user_id=current_user.id, arac_id=arac_id, durum='onaylandı', iptal_edildi=False).first()
    yorum_yapabilir = False
    if kiralama and (not kiralama.bitis_tarihi or kiralama.bitis_tarihi > datetime.utcnow()):
        yorum_yapabilir = Yorum.query.filter_by(user_id=current_user.id, arac_id=arac_id).count() == 0
    if request.method == "POST" and yorum_yapabilir:
        puan = int(request.form["puan"])
        yorum_text = request.form["yorum"]
        yeni_yorum = Yorum(user_id=current_user.id, arac_id=arac_id, puan=puan, yorum=yorum_text)
        db.session.add(yeni_yorum)
        db.session.commit()
        flash("Yorumunuz eklendi!", "success")
        return redirect(url_for("arac_detay", arac_id=arac_id))
    return render_template("arac_detay.html", arac=arac, yorumlar=yorumlar, ort_puan=ort_puan, yorum_yapabilir=yorum_yapabilir)

@app.route("/kirala/<int:arac_id>", methods=["GET", "POST"])
@login_required
def kirala(arac_id):
    arac = Arac.query.get_or_404(arac_id)
    if arac.kirada:
        flash("Bu araç zaten kiralanmış!", "danger")
        return redirect(url_for("panel"))
    if request.method == "POST":
        kart_no = request.form["kart_no"]
        isim = request.form["isim"]
        son_kullanma = request.form["son_kullanma"]
        cvv = request.form["cvv"]
        gun_sayisi = int(request.form.get("gun_sayisi", 1))
        if not (kart_no and isim and son_kullanma and cvv and gun_sayisi > 0):
            flash("Tüm ödeme alanlarını doldurun!", "danger")
            return redirect(url_for("kirala", arac_id=arac_id))
        toplam_tutar = arac.fiyat * gun_sayisi
        bitis_tarihi = datetime.utcnow() + timedelta(days=gun_sayisi)
        kiralama = Kiralama(user_id=current_user.id, arac_id=arac.id, tutar=toplam_tutar, gun_sayisi=gun_sayisi, bitis_tarihi=bitis_tarihi, durum='beklemede')
        db.session.add(kiralama)
        db.session.commit()
        flash("Kiralama talebiniz alınmıştır. Onay bekliyor.", "info")
        return redirect(url_for("panel"))
    return render_template("odeme.html", arac=arac)

@app.route("/arac_ekle", methods=["GET", "POST"])
@login_required
def arac_ekle():
    if current_user.rol != "admin":
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        marka = request.form["marka"]
        model = request.form["model"]
        fiyat = int(request.form["fiyat"])
        resim = request.files.get("resim")
        resim_url = None
        if resim and resim.filename:
            filename = secure_filename(resim.filename)
            yol = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resim.save(yol)
            resim_url = f"/static/uploads/{filename}"
        yeni_arac = Arac(
            marka=marka,
            model=model,
            fiyat=fiyat,
            kirada=False,
            resim_url=resim_url
        )
        db.session.add(yeni_arac)
        db.session.commit()
        flash("Araç başarıyla eklendi!", "success")
        return redirect(url_for("index"))
    return render_template("arac_ekle.html")

@app.route("/panel")
@login_required
def panel():
    from datetime import datetime as dt
    # Kiralama süresi biten araçları otomatik müsait yap
    for k in Kiralama.query.filter_by(durum='onaylandı', iptal_edildi=False).all():
        if k.bitis_tarihi and k.bitis_tarihi < dt.utcnow() and k.arac.kirada:
            k.arac.kirada = False
            db.session.commit()
    q = request.args.get('q', '').strip().lower()
    fmin = request.args.get('fmin')
    fmax = request.args.get('fmax')
    durum = request.args.get('durum')
    araclar = Arac.query
    if q:
        araclar = araclar.filter((Arac.marka.ilike(f'%{q}%')) | (Arac.model.ilike(f'%{q}%')))
    if fmin:
        araclar = araclar.filter(Arac.fiyat >= int(fmin))
    if fmax:
        araclar = araclar.filter(Arac.fiyat <= int(fmax))
    if durum == 'müsait':
        araclar = araclar.filter(Arac.kirada == False)
    elif durum == 'kirada':
        araclar = araclar.filter(Arac.kirada == True)
    araclar = araclar.all()
    kiralamalar = Kiralama.query.filter_by(user_id=current_user.id).order_by(Kiralama.tarih.desc()).all()
    return render_template("panel.html", araclar=araclar, kiralamalar=kiralamalar, now=dt.utcnow, request=request)

@app.route("/admin")
@login_required
def admin_panel():
    if current_user.rol != "admin":
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("index"))
    from datetime import datetime as dt
    # Kiralama süresi biten araçları otomatik müsait yap
    for k in Kiralama.query.filter_by(durum='onaylandı', iptal_edildi=False).all():
        if k.bitis_tarihi and k.bitis_tarihi < dt.utcnow() and k.arac.kirada:
            k.arac.kirada = False
            db.session.commit()
    toplam_arac = Arac.query.count()
    toplam_kullanici = User.query.filter_by(rol='musteri').count()
    toplam_kiralama = Kiralama.query.count()
    toplam_gelir = db.session.query(func.sum(Kiralama.tutar)).scalar() or 0
    # En çok kiralanan araç
    en_cok_kiralanan = db.session.query(
        Arac.marka, Arac.model, func.count(Kiralama.id).label('kiralama_sayisi')
    ).join(Kiralama).group_by(Arac.id).order_by(desc('kiralama_sayisi')).first()
    # En çok harcayan müşteri
    en_cok_harcayan = db.session.query(
        User.isim, User.email, func.sum(Kiralama.tutar).label('toplam_harcama')
    ).join(Kiralama).group_by(User.id).order_by(desc('toplam_harcama')).first()
    araclar = Arac.query.all()
    kullanicilar = User.query.all()
    kiralamalar = Kiralama.query.order_by(Kiralama.tarih.desc()).all()
    yorumlar = Yorum.query.order_by(Yorum.tarih.desc()).all()
    # Grafik verileri
    bar_labels = [f"{a.marka} {a.model}" for a in araclar]
    bar_data = [len(a.kiralamalar) for a in araclar]
    pie_data = [sum([k.tutar for k in a.kiralamalar]) for a in araclar]
    return render_template(
        "admin_panel.html",
        toplam_arac=toplam_arac,
        toplam_kullanici=toplam_kullanici,
        toplam_kiralama=toplam_kiralama,
        toplam_gelir=toplam_gelir,
        en_cok_kiralanan=en_cok_kiralanan,
        en_cok_harcayan=en_cok_harcayan,
        araclar=araclar,
        kullanicilar=kullanicilar,
        kiralamalar=kiralamalar,
        yorumlar=yorumlar,
        bar_labels=bar_labels,
        bar_data=bar_data,
        pie_data=pie_data,
        now=dt.utcnow
    )

@app.route("/arac_duzenle/<int:arac_id>", methods=["GET", "POST"])
@login_required
def arac_duzenle(arac_id):
    if current_user.rol != "admin":
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("index"))
    arac = Arac.query.get_or_404(arac_id)
    if request.method == "POST":
        arac.marka = request.form["marka"]
        arac.model = request.form["model"]
        arac.fiyat = int(request.form["fiyat"])
        resim = request.files.get("resim")
        if resim and resim.filename:
            filename = secure_filename(resim.filename)
            yol = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resim.save(yol)
            arac.resim_url = f"/static/uploads/{filename}"
        db.session.commit()
        flash("Araç güncellendi!", "success")
        return redirect(url_for("admin_panel"))
    return render_template("arac_duzenle.html", arac=arac)

@app.route("/arac_sil/<int:arac_id>", methods=["POST"])
@login_required
def arac_sil(arac_id):
    if current_user.rol != "admin":
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("index"))
    arac = Arac.query.get_or_404(arac_id)
    db.session.delete(arac)
    db.session.commit()
    flash("Araç silindi!", "success")
    return redirect(url_for("admin_panel"))

@app.route("/kullanici_duzenle/<int:user_id>", methods=["GET", "POST"])
@login_required
def kullanici_duzenle(user_id):
    if current_user.rol != "admin":
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("index"))
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.isim = request.form["isim"]
        user.email = request.form["email"]
        user.rol = request.form["rol"]
        db.session.commit()
        flash("Kullanıcı güncellendi!", "success")
        return redirect(url_for("admin_panel"))
    return render_template("kullanici_duzenle.html", user=user)

@app.route("/kullanici_sil/<int:user_id>", methods=["POST"])
@login_required
def kullanici_sil(user_id):
    if current_user.rol != "admin":
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("index"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Kullanıcı silindi!", "success")
    return redirect(url_for("admin_panel"))

@app.route("/kiralama_iptal/<int:kiralama_id>", methods=["POST"])
@login_required
def kiralama_iptal(kiralama_id):
    kiralama = Kiralama.query.get_or_404(kiralama_id)
    if kiralama.user_id != current_user.id and current_user.rol != "admin":
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for("panel"))
    if kiralama.iptal_edildi:
        flash("Bu kiralama zaten iptal edilmiş.", "warning")
        return redirect(url_for("panel"))
    kiralama.iptal_edildi = True
    kiralama.arac.kirada = False
    db.session.commit()
    flash("Kiralama iptal edildi. Araç tekrar müsait.", "success")
    if current_user.rol == "admin":
        return redirect(url_for("admin_panel"))
    return redirect(url_for("panel"))

@app.route("/kiralama_onayla/<int:kiralama_id>", methods=["POST"])
@login_required
def kiralama_onayla(kiralama_id):
    if current_user.rol != "admin":
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for("admin_panel"))
    kiralama = Kiralama.query.get_or_404(kiralama_id)
    if kiralama.durum != 'beklemede':
        flash("Bu kiralama zaten işleme alınmış.", "warning")
        return redirect(url_for("admin_panel"))
    kiralama.durum = 'onaylandı'
    kiralama.arac.kirada = True
    db.session.commit()
    flash("Kiralama onaylandı! Araç kirada.", "success")
    return redirect(url_for("admin_panel"))

@app.route("/kiralama_reddet/<int:kiralama_id>", methods=["POST"])
@login_required
def kiralama_reddet(kiralama_id):
    if current_user.rol != "admin":
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for("admin_panel"))
    kiralama = Kiralama.query.get_or_404(kiralama_id)
    if kiralama.durum != 'beklemede':
        flash("Bu kiralama zaten işleme alınmış.", "warning")
        return redirect(url_for("admin_panel"))
    kiralama.durum = 'reddedildi'
    db.session.commit()
    flash("Kiralama reddedildi.", "info")
    return redirect(url_for("admin_panel"))

@app.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    if request.method == "POST":
        isim = request.form["isim"]
        email = request.form["email"]
        eski_sifre = request.form.get("eski_sifre")
        yeni_sifre = request.form.get("yeni_sifre")
        yeni_sifre_tekrar = request.form.get("yeni_sifre_tekrar")
        # Email başka kullanıcıya ait mi kontrolü
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash("Bu email başka bir kullanıcıya ait!", "danger")
            return redirect(url_for("profil"))
        current_user.isim = isim
        current_user.email = email
        # Şifre değişikliği istenmişse
        if eski_sifre or yeni_sifre or yeni_sifre_tekrar:
            if not (eski_sifre and yeni_sifre and yeni_sifre_tekrar):
                flash("Şifre değiştirmek için tüm şifre alanlarını doldurun!", "danger")
                return redirect(url_for("profil"))
            if not check_password_hash(current_user.sifre, eski_sifre):
                flash("Mevcut şifreniz yanlış!", "danger")
                return redirect(url_for("profil"))
            if yeni_sifre != yeni_sifre_tekrar:
                flash("Yeni şifreler eşleşmiyor!", "danger")
                return redirect(url_for("profil"))
            current_user.sifre = generate_password_hash(yeni_sifre)
        db.session.commit()
        flash("Profiliniz güncellendi!", "success")
        return redirect(url_for("profil"))
    return render_template("profil.html")

@app.route("/yorum_sil/<int:yorum_id>", methods=["POST"])
@login_required
def yorum_sil(yorum_id):
    yorum = Yorum.query.get_or_404(yorum_id)
    if current_user.rol != "admin":
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for("admin_panel"))
    db.session.delete(yorum)
    db.session.commit()
    flash("Yorum silindi!", "success")
    return redirect(url_for("admin_panel"))

@app.route("/favori_ekle/<int:arac_id>", methods=["POST"])
@login_required
def favori_ekle(arac_id):
    if Favori.query.filter_by(user_id=current_user.id, arac_id=arac_id).first():
        return jsonify({"success": False, "message": "Zaten favorilerde."})
    try:
        fav = Favori(user_id=current_user.id, arac_id=arac_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({"success": True, "message": "Favorilere eklendi."})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "message": "Hata oluştu."})

@app.route("/favori_cikar/<int:arac_id>", methods=["POST"])
@login_required
def favori_cikar(arac_id):
    fav = Favori.query.filter_by(user_id=current_user.id, arac_id=arac_id).first()
    if not fav:
        return jsonify({"success": False, "message": "Favoride değil."})
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"success": True, "message": "Favorilerden çıkarıldı."})

def favori_mi(user_id, arac_id):
    return Favori.query.filter_by(user_id=user_id, arac_id=arac_id).first() is not None

if __name__ == "__main__":
    app.run(debug=True) 