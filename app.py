from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import random
import os

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'smartlite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fleurs-bleues-et-roses-123'

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    humeur = db.Column(db.String(10))
    energie = db.Column(db.Integer)
    sommeil = db.Column(db.Float)
    activite = db.Column(db.String(50))

with app.app_context():
    db.create_all()

def get_humour_message(energie, nouveau_venu=False):
    if nouveau_venu:
        return "Bienvenue dans SmartLite ! Dis-moi comment tu te sens aujourd'hui. ✨"
    
    if energie <= 3:
        return random.choice([
            "Tu es officiellement un zombie. 🧟",
            "Même une plante en plastique a plus d'énergie que toi.",
            "Batterie faible. Branche-toi à un café, vite !"
        ])
    elif energie <= 7:
        return random.choice([
            "Pas mal ! Tu es presque un être humain fonctionnel. 🤖",
            "La moyenne, c'est bien. Ni génie, ni paresseux.",
            "On sent que le moteur tourne, mais ne tente pas un marathon."
        ])
    else:
        return random.choice([
            "Wouah ! Tu as mangé quoi au petit-déjeuner ? 🚀",
            "Énergie de super-héros. Tu fais de l'ombre aux autres.",
            "Tu es prêt à conquérir le monde !"
        ])

@app.route('/')
def index():
    # On récupère les 30 dernières entrées pour ne pas surcharger le graph
    entries = Entry.query.order_by(Entry.date.desc()).limit(30).all()
    
    graph_html = ""
    if entries:
        entries_reversed = entries[::-1]
        dates = [e.date.strftime("%d/%m") for e in entries_reversed]
        energies = [e.energie for e in entries_reversed]
        sommeils = [e.sommeil for e in entries_reversed]
        
        # Création d'un graphique combiné Énergie + Sommeil
        fig = go.Figure()
        
        # Courbe Énergie
        fig.add_trace(go.Scatter(x=dates, y=energies, name="Énergie",
                                 line=dict(color='#ff69b4', width=3),
                                 marker=dict(size=8)))
        
        # Courbe Sommeil (sur un axe invisible ou superposé)
        fig.add_trace(go.Scatter(x=dates, y=sommeils, name="Sommeil (h)",
                                 line=dict(color='#d0e1ff', width=3, dash='dash')))

        fig.update_layout(
            title="Patterns Énergie vs Sommeil 🌙",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        graph_html = pio.to_html(fig, full_html=False)

    # Gestion du message d'accueil
    nouveau = len(entries) == 0
    last_energy = entries[0].energie if entries else 5
    message = get_humour_message(last_energy, nouveau_venu=nouveau)

    return render_template('index.html', entries=entries, graph=graph_html, message=message)

@app.route('/ajouter', methods=['POST'])
def ajouter():
    try:
        humeur = request.form.get('humeur')
        # Utilisation de .get avec valeur par défaut pour éviter les crashs
        energie = int(request.form.get('energie', 5))
        sommeil = float(request.form.get('sommeil', 0).replace(',', '.')) # Gère les virgules
        activite = request.form.get('activite')

        nouvelle_entree = Entry(humeur=humeur, energie=energie, sommeil=sommeil, activite=activite)
        db.session.add(nouvelle_entree)
        db.session.commit()
    except Exception as e:
        print(f"Erreur lors de l'ajout : {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)