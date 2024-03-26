from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db

runners = Blueprint('runners', __name__)

@runners.route('/runner', methods=['GET', 'POST'])
def runner():
    if request.method == 'POST':
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ygh_runners (first_name, last_name, time_1600_pr, time_3200_pr, time_800_pr, time_5k_pr, runner_mile_split_url, grad_year, gender) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            request.form['first_name'],
                            request.form['last_name'],
                            request.form['time_1600_pr'],
                            request.form['time_3200_pr'],
                            request.form['time_800_pr'],
                            request.form['time_5k_pr'],
                            request.form['runner_mile_split_url'],
                            request.form['grad_year'],
                            request.form['gender'],
                        ))
            conn.commit()
        flash('Runner added successfully')
        return redirect(url_for('runners.runner'))
    year = request.args.get('year')
    runners_by_year_gender = get_runners(year)
    return render_template('runners.html', runners_by_year_gender=runners_by_year_gender)

@runners.route('/update_runner/<runner_id>/', methods=['POST'])
def update_runner(runner_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE ygh_runners 
            SET first_name=%s, last_name=%s, time_800_pr=%s, time_1600_pr=%s, time_3200_pr=%s, time_5k_pr=%s, runner_mile_split_url=%s 
            WHERE runner_id=%s
        """, (
            request.form['first_name'],
            request.form['last_name'],
            request.form['time_800_pr'],
            request.form['time_1600_pr'],
            request.form['time_3200_pr'],
            request.form['time_5k_pr'],
            request.form['runner_mile_split_url'],
            runner_id
        ))
        conn.commit()
    flash('Runner updated successfully')
    return redirect(url_for('runners.runner'))

@runners.route('/delete_runner/<runner_id>/', methods=['POST'])
def delete_runner(runner_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ygh_runners WHERE runner_id=%s", (runner_id,))
        conn.commit()
    flash('Runner deleted successfully')
    return redirect(url_for('runners.runner'))

#### FUNCTIONS ########################################################################################################
#######################################################################################################################

def get_runners(year=None):
    conn = get_db()
    with conn.cursor() as cur:
        if year:
            cur.execute("SELECT * FROM ygh_runners WHERE grad_year = %s ORDER BY grad_year DESC, gender", (year,))
        else:
            cur.execute("SELECT * FROM ygh_runners ORDER BY grad_year DESC, gender")
        runners = cur.fetchall()
    runners_by_year_gender = {}
    for runner in runners:
        key = (runner['grad_year'], runner['gender'])
        if key not in runners_by_year_gender:
            runners_by_year_gender[key] = []
        runners_by_year_gender[key].append(runner)
    return runners_by_year_gender

