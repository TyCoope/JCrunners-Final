from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db_connect import get_db
from itertools import groupby
from flask import jsonify

race_times = Blueprint('race_times', __name__)

@race_times.route('/race_time/<race_id>', methods=['GET', 'POST'])
def race_time(race_id):
    rosters = fetch_rosters_from_db()
    race_types = fetch_race_types_from_db()
    if request.method == 'POST':
        # Retrieve form data
        race_type_id = request.form['race_type_id']

        # Map race_type_id to the corresponding field in the runners table
        race_type_field_mapping = {
            '1': 'time_800_pr',
            '2': 'time_1600_pr',
            '4': 'time_3200_pr',
            '3': 'time_5k_pr'
        }

        # Iterate over the form data
        for key, value in request.form.items():
            if key.startswith('time_') and value:  # Check if value is not empty
                runner_id = key.split('_')[1]
                duration_time = value

                # Insert new race time into the database
                conn = get_db()
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO race_detail (runner_id, race_id, race_type_id, duration_time)
                        VALUES (%s, %s, %s, %s)
                    """, (runner_id, race_id, race_type_id, duration_time))

                    # Fetch the runner's profile
                    cur.execute("SELECT * FROM runners WHERE runner_id=%s", (runner_id,))
                    runner = cur.fetchone()

                    # Get the field to update based on the race_type_id
                    field_to_update = race_type_field_mapping[race_type_id]

                    # Check if the field is None or empty or if the new time is lower
                    if runner[field_to_update] in [None, ''] or runner[field_to_update] > duration_time:
                        # If either condition is true, update the runner's profile
                        cur.execute(f"UPDATE runners SET {field_to_update}=%s WHERE runner_id=%s",
                                    (duration_time, runner_id))
                    conn.commit()

        # Redirect to the same page to see the updated race times
        return redirect(url_for('race_times.race_time', race_id=race_id))


    else:  # GET method
        race_info = fetch_race_info_from_db(race_id)
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    runners.runner_id,
                    runners.first_name,
                    runners.last_name,
                    runners.gender,
                    race_detail.race_detail_id,
                    race_detail.race_id,
                    race_detail.race_type_id,
                    race_detail.duration_time,
                    race.race_name,
                    race_type.race_type_name,
                    race_type.rank_order
                FROM
                    runners
                JOIN
                    race_detail ON runners.runner_id = race_detail.runner_id
                JOIN
                    race ON race_detail.race_id = race.race_id
                JOIN
                    race_type ON race_detail.race_type_id = race_type.race_type_id
                WHERE
                    race.race_id = %s
                ORDER BY
                    race_type.rank_order,
                    runners.gender,
                    race_detail.duration_time;
            """, (race_id,))
            results = [dict(row) for row in cur.fetchall()]
        # Group the results by race_type_name and then by gender
        grouped_results = {}
        for result in results:
            race_type_name = result['race_type_name']
            if race_type_name not in grouped_results:
                grouped_results[race_type_name] = {}
            gender = result['gender']
            if gender not in grouped_results[race_type_name]:
                grouped_results[race_type_name][gender] = []
            grouped_results[race_type_name][gender].append(result)

        # Sort the groups by gender and then by duration_time
        for race_type, gender_groups in grouped_results.items():
            for gender, runners in gender_groups.items():
                runners.sort(key=lambda x: x['duration_time'])

        return render_template('race_times.html', results=grouped_results, race_info=race_info, rosters=rosters,
                               race_types=race_types)

@race_times.route('/add_race_time/<race_id>', methods=['GET'])
def add_race_time(race_id):
    # Fetch the runners based on the roster_id from the GET parameters
    roster_id = request.args.get('roster_id')
    runners = []
    if roster_id is not None:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT runners.*
                FROM runners
                JOIN roster_detail ON runners.runner_id = roster_detail.runner_id
                WHERE roster_detail.roster_id = %s
            """, (roster_id,))
            runners = [dict(row) for row in cur.fetchall()]

    # Return the runners as a JSON response
    return jsonify(runners)

@race_times.route('/delete_race_time/<race_detail_id>/<race_id>', methods=['POST'])
def delete_race_time(race_detail_id, race_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM race_detail WHERE race_detail_id = %s", (race_detail_id,))
        conn.commit()

    return redirect(url_for('race_times.race_time', race_id=race_id))

@race_times.route('/update_race_time/<race_detail_id>/<race_id>', methods=['POST'])
def update_race_time(race_detail_id, race_id):
    runner_id, race_type_id = fetch_runner_id_from_db(race_detail_id)

    duration_time = request.form['duration_time']
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE race_detail SET duration_time = %s WHERE race_detail_id = %s", (duration_time, race_detail_id))
        conn.commit()

        # Map race_type_id to the corresponding field in the runners table
        race_type_field_mapping = {
            1: 'time_800_pr',
            2: 'time_1600_pr',
            4: 'time_3200_pr',
            3: 'time_5k_pr'
        }

        # Fetch the runner's profile
        cur.execute("SELECT * FROM runners WHERE runner_id=%s", (runner_id,))
        runner = cur.fetchone()

        # Get the field to update based on the race_type_id
        field_to_update = race_type_field_mapping[race_type_id]

        # Check if the field is None or empty or if the new time is lower
        if runner[field_to_update] in [None, ''] or runner[field_to_update] > duration_time:
            # If either condition is true, update the runner's profile
            cur.execute(f"UPDATE runners SET {field_to_update}=%s WHERE runner_id=%s",
                        (duration_time, runner_id))
        conn.commit()

    return redirect(url_for('race_times.race_time', race_id=race_id))


#### FUNCTIONS ########################################################################################################
#######################################################################################################################

def fetch_rosters_from_db():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM rosters ORDER BY roster_year DESC")
        return cur.fetchall()

def fetch_race_types_from_db():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM race_type")
        return cur.fetchall()

def fetch_race_info_from_db(race_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT race_id, race_name, EXTRACT(YEAR FROM race_date) as race_year FROM race WHERE race_id = %s", (race_id,))
        return cur.fetchone()

def fetch_runner_id_from_db(race_detail_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT runner_id, race_type_id FROM race_detail WHERE race_detail_id = %s", (race_detail_id,))
        result = cur.fetchone()
        print(result)
        return result['runner_id'],result['race_type_id']