from flask import Flask, render_template
from src.database.database import SessionLocal
from src.statistics.standings_calculator import StandingsCalculator
from src.statistics.scorers_calculator import TopScorersCalculator

app = Flask(__name__)


@app.route('/')
def index():
    db = SessionLocal()
    try:
        # Get all statistics
        standings_calc = StandingsCalculator(db)
        scorers_calc = TopScorersCalculator(db)

        data = {
            'standings': standings_calc.calculate_standings(),
            'scorers': scorers_calc.calculate_top_scorers()
        }

        return render_template('index.html', data=data)
    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)