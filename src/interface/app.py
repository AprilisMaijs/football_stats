from flask import Flask, render_template, jsonify
from src.database.database import SessionLocal, init_db, engine
from src.database.models import Base
from src.statistics.standings_calculator import StandingsCalculator
from src.statistics.scorers_calculator import TopScorersCalculator
from src.statistics.substitutions_calculator import SubstitutionCalculator
from src.statistics.popular_goals_calculator import PopularGoalsCalculator
from src.initialize import initialize_database

app = Flask(__name__)

@app.route('/')
def index():
    db = SessionLocal()
    try:
        standings_calc = StandingsCalculator(db)
        scorers_calc = TopScorersCalculator(db)
        substitutions_calc = SubstitutionCalculator(db)
        popular_goals_calc = PopularGoalsCalculator(db)

        data = {
            'standings': standings_calc.calculate_standings(),
            'scorers': scorers_calc.calculate_top_scorers(),
            'substitutions': substitutions_calc.calculate_substitution_stats(),
            'goals': popular_goals_calc.calculate_popular_goals()
        }
        return render_template('index.html', data=data)
    finally:
        db.close()

@app.route('/api/flush', methods=['POST'])
def flush_data():
    try:
        Base.metadata.drop_all(bind=engine)
        init_db()
        return jsonify({"status": "success", "message": "Database flushed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reload', methods=['POST'])
def reload_data():
    try:
        initialize_database()
        return jsonify({"status": "success", "message": "Data reloaded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)