from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db

races = Blueprint('races', __name__)

@races.route('/race', methods=['GET', 'POST'])
def race():
    if request.method == 'POST':
        race_location = request.form['race_location']
        race_mile_split_url = request.form['race_mile_split_url']
        race_name = request.form['race_name']
        race_date = request.form['race_date']
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ygh_race (race_name, race_date, race_location, race_mile_split_url) VALUES (%s, %s, %s, %s)",
                        (
                            race_name,
                            race_date,
                            race_location,
                            race_mile_split_url
                        ))
            conn.commit()
        flash('Race added successfully')
        return redirect(url_for('races.race'))

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT EXTRACT(YEAR FROM race_date) as year, race_id, race_name, race_date, race_location, race_mile_split_url FROM ygh_race ORDER BY race_date")
        races_by_year = {}
        for row in cur.fetchall():
            year = row['year']
            if year not in races_by_year:
                races_by_year[year] = []
            races_by_year[year].append(row)
    return render_template('races.html', races_by_year=races_by_year)


@races.route('/update_race/<race_id>/', methods=['POST'])
def update_race(race_id):
    race_name = request.form['race_name']
    race_date = request.form['race_date']
    race_location = request.form['race_location']
    race_mile_split_url = request.form['race_mile_split_url']
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE ygh_race SET race_name=%s, race_date=%s, race_location=%s, race_mile_split_url=%s WHERE race_id=%s",
                    (
                        race_name,
                        race_date,
                        race_location,
                        race_mile_split_url,
                        race_id
                    ))
        conn.commit()
    flash('Race updated successfully')
    return redirect(url_for('races.race'))

@races.route('/delete_race/<race_id>/', methods=['POST'])
def delete_race(race_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ygh_race WHERE race_id=%s", (race_id,))
        conn.commit()
    flash('Race deleted successfully')
    return redirect(url_for('races.race'))

@races.route('/add_race_times/<race_id>/', methods=['GET', 'POST'])
def add_race_times(race_id):
    pass
