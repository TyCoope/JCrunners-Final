from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
from datetime import datetime

rosters = Blueprint('rosters', __name__)

@rosters.route('/roster', methods=['GET', 'POST'])
def roster():
    if request.method == 'POST':
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ygh_rosters (roster_year, roster_season, gender) "
                        "VALUES (%s, %s, %s)",
                        (
                            request.form['roster_year'],
                            request.form['roster_season'],
                            request.form['gender'],
                        ))
            conn.commit()
        flash('Roster added successfully')
        return redirect(url_for('rosters.roster'))
    rosters = get_rosters()
    return render_template('rosters.html', rosters=rosters)

@rosters.route('/update_roster/<roster_id>/', methods=['POST'])
def update_roster(roster_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE ygh_rosters SET roster_year=%s, roster_season=%s, gender=%s WHERE roster_id=%s",
                    (
                        request.form['roster_year'],
                        request.form['roster_season'],
                        request.form['gender'],
                        roster_id)
                    )
        conn.commit()
    flash('Roster updated successfully')
    return redirect(url_for('rosters.roster'))

@rosters.route('/delete_roster/<roster_id>/', methods=['POST'])
def delete_roster(roster_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ygh_rosters WHERE roster_id=%s", (roster_id,))
        conn.commit()
    flash('Roster deleted successfully')
    return redirect(url_for('rosters.roster'))

@rosters.route('/roster_details/<roster_id>/', methods=['GET', 'POST'])
def roster_details(roster_id):
    if request.method == 'POST':
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ygh_roster_detail (roster_id, runner_id) "
                        "VALUES (%s, %s)",
                        (
                            roster_id,
                            request.form['runner_id'],
                        ))
            conn.commit()
        flash('Runner added to roster successfully')
        return redirect(url_for('rosters.roster_details'))
    roster = get_roster_info(roster_id)
    runner_drop = runner_dropdown(roster_id)
    current_roster = get_roster_by_details(roster_id)
    print(current_roster)
    return render_template('roster_details.html', current_roster=current_roster, roster=roster, runner_drop=runner_drop)

@rosters.route('/delete_runner_from_roster/<roster_detail_id>/<roster_id>/', methods=['POST'])
def delete_runner_from_roster(roster_detail_id, roster_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ygh_roster_detail WHERE roster_detail_id=%s", (roster_detail_id))
        conn.commit()
    flash('Runner removed from roster successfully')
    return redirect(url_for('rosters.roster_details', roster_id=roster_id))

@rosters.route('/add_runner_to_roster/<roster_id>/', methods=['POST'])
def add_runner_to_roster(roster_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO ygh_roster_detail (roster_id, runner_id) "
                    "VALUES (%s, %s)",
                    (
                        roster_id,
                        request.form['runner_id'],
                    ))
        conn.commit()
    flash('Runner added to roster successfully')
    return redirect(url_for('rosters.roster_details', roster_id=roster_id))

#### FUNCTIONS ########################################################################################################
#######################################################################################################################
# loads the current rosters
def get_rosters():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ygh_rosters ORDER BY roster_year DESC, roster_season ASC")
        rosters = cur.fetchall()
    return rosters

# gets the current roster details
def get_roster_info(roster_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ygh_rosters WHERE roster_id=%s", (roster_id,))
        roster = cur.fetchone()
    return roster

# gets all the runners in a specific roster
def get_roster_by_details(roster_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT RD.roster_detail_id, R.first_name, R.last_name, R.grad_year, RD.roster_id "
                    "FROM ygh_runners R "
                    "JOIN ygh_roster_detail RD ON R.runner_id = RD.runner_id "
                    "WHERE RD.roster_id = %s", (roster_id,))
        roster_details = cur.fetchall()
    return roster_details

# function to select runners for the dropdown in the add modal
def runner_dropdown(roster_id):
    current_year = datetime.now().year
    future_year = current_year + 7
    conn = get_db()
    with conn.cursor() as cur:
        # Fetch the gender of the roster
        cur.execute("SELECT gender FROM ygh_rosters WHERE roster_id = %s", (roster_id,))
        roster_gender_result = cur.fetchone()
        print(roster_gender_result)
        if roster_gender_result is None or not isinstance(roster_gender_result, dict):
            return []
        roster_gender = roster_gender_result['gender']
        print(roster_gender)



        # Fetch all runners that match the gender of the roster
        cur.execute("""
            SELECT R.runner_id, R.first_name, R.last_name 
            FROM ygh_runners R 
            WHERE R.grad_year BETWEEN %s AND %s 
            AND R.gender = %s 
            AND R.runner_id NOT IN ( 
                SELECT RD.runner_id 
                FROM ygh_roster_detail RD 
                WHERE RD.roster_id = %s 
            )
        """, (current_year, future_year, roster_gender, roster_id))
        runner_drop = cur.fetchall()
    return runner_drop