from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db

results = Blueprint('results', __name__)

@results.route('/result')
def result():
    male_runners_800 = get_best_runners("Male", "time_800_pr")
    this_season_male_runners_800 = this_season_best_runners("Male", "time_800_pr")
    female_runners_800 = get_best_runners("Female", "time_800_pr")
    male_runners_1600 = get_best_runners("Male", "time_1600_pr")
    female_runners_1600 = get_best_runners("Female", "time_1600_pr")
    male_runners_3200 = get_best_runners("Male", "time_3200_pr")
    female_runners_3200 = get_best_runners("Female", "time_3200_pr")
    male_runners_5k = get_best_runners("Male", "time_5k_pr")
    female_runners_5k = get_best_runners("Female", "time_5k_pr")
    male_runners_2024 = get_male_runners_2024()  # Call the function here
    female_runners_2024 = get_female_runners_2024()  # Call the function here
    return render_template('results.html',
                           male_runners_2024=male_runners_2024,  # Pass the result of the function call
                           female_runners_2024=female_runners_2024,  # Pass the result of the function call
                           male_runners_800=male_runners_800,
                           female_runners_800=female_runners_800,
                           male_runners_1600=male_runners_1600,
                           female_runners_1600=female_runners_1600,
                           male_runners_3200=male_runners_3200,
                           female_runners_3200=female_runners_3200,
                           male_runners_5k=male_runners_5k,
                           female_runners_5k=female_runners_5k,
                           this_season_male_runners_800=this_season_male_runners_800
                           )

def get_best_runners(gender, distance):
    conn = get_db()
    with conn.cursor() as cur:
        table_name = "runners"  # replace with your actual table name
        sql = f"""
            SELECT runner_id, grad_year, {distance}, first_name, last_name
            FROM {table_name}
            WHERE gender = %s AND {distance} > 0
            ORDER BY {distance} ASC
            LIMIT 10
        """
        cur.execute(sql, (gender,))
        best_runners = cur.fetchall()

    # Add ranking in Python
    for i, runner in enumerate(best_runners, start=1):
        runner['runner_ranking'] = i

    return best_runners

def this_season_best_runners(gender, distance):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT roster_id FROM rosters WHERE gender = %s ORDER BY roster_year DESC LIMIT 1", (gender,))
        roster_id = cur.fetchone()['roster_id']

        sql = f"""
            SELECT runners.runner_id, grad_year, {distance}, first_name, last_name
            FROM runners
            JOIN roster_detail ON runners.runner_id = roster_detail.runner_id
            WHERE gender = %s AND {distance} > 0 AND roster_detail.roster_id = %s
            ORDER BY {distance} ASC
        """
        cur.execute(sql, (gender, roster_id))
        best_runners = cur.fetchall()

        cur.execute("SELECT * from roster_detail WHERE roster_id = %s", (roster_id,))
        roster_detail = cur.fetchall()

    # Convert roster_detail to a set for faster lookup
    roster_detail_set = set(row['runner_id'] for row in roster_detail)

    # Add 'is_in_latest_roster' key to each runner in male_runners_800
    for runner in best_runners:
        runner['is_in_latest_roster'] = 1 if runner['runner_id'] in roster_detail_set else 0

    # Add ranking in Python
    for i, runner in enumerate(best_runners, start=1):
        runner['runner_ranking'] = i

    return best_runners

def get_male_runners_2024():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT runners.first_name, runners.last_name,
                   MIN(case when race_type.race_type_name = '800m' then race_detail.duration_time end) as time_800_pr,
                   MIN(case when race_type.race_type_name = '1600m' then race_detail.duration_time end) as time_1600_pr,
                   MIN(case when race_type.race_type_name = '3200m' then race_detail.duration_time end) as time_3200_pr,
                   MIN(case when race_type.race_type_name = '5k' then race_detail.duration_time end) as time_5k_pr
            FROM runners
            JOIN race_detail ON runners.runner_id = race_detail.runner_id
            JOIN race ON race_detail.race_id = race.race_id
            JOIN race_type ON race_detail.race_type_id = race_type.race_type_id
            WHERE runners.gender = 'Male' AND EXTRACT(YEAR FROM race.race_date) = 2024
            GROUP BY runners.runner_id
        """)
        male_runners_2024 = cur.fetchall()

    # Add ranking in Python for each race
    for i, runner in enumerate(sorted(male_runners_2024, key=lambda x: x['time_800_pr'] if x['time_800_pr'] is not None else '9999:59:59'), start=1):
        runner['time_800_rank'] = i
    for i, runner in enumerate(sorted(male_runners_2024, key=lambda x: x['time_1600_pr'] if x['time_1600_pr'] is not None else '9999:59:59'), start=1):
        runner['time_1600_rank'] = i
    for i, runner in enumerate(sorted(male_runners_2024, key=lambda x: x['time_3200_pr'] if x['time_3200_pr'] is not None else '9999:59:59'), start=1):
        runner['time_3200_rank'] = i

    # Calculate overall rank as the average of the individual race ranks
    for runner in male_runners_2024:
        runner['overall_rank'] = sum([runner['time_800_rank'], runner['time_1600_rank'], runner['time_3200_rank']]) / 3

    # Sort runners by overall rank and assign place rank
    sorted_runners = sorted(male_runners_2024, key=lambda x: x['overall_rank'])
    for i, runner in enumerate(sorted_runners, start=1):
        runner['place_rank'] = i

    return sorted_runners

def get_male_runners_2024():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT runners.first_name, runners.last_name,
                   MIN(case when race_type.race_type_name = '800m' then race_detail.duration_time end) as time_800_pr,
                   MIN(case when race_type.race_type_name = '1600m' then race_detail.duration_time end) as time_1600_pr,
                   MIN(case when race_type.race_type_name = '3200m' then race_detail.duration_time end) as time_3200_pr,
                   MIN(case when race_type.race_type_name = '5k' then race_detail.duration_time end) as time_5k_pr
            FROM runners
            JOIN race_detail ON runners.runner_id = race_detail.runner_id
            JOIN race ON race_detail.race_id = race.race_id
            JOIN race_type ON race_detail.race_type_id = race_type.race_type_id
            WHERE runners.gender = 'Male' AND EXTRACT(YEAR FROM race.race_date) = 2024
            GROUP BY runners.runner_id
        """)
        male_runners_2024 = cur.fetchall()

    # Add ranking in Python for each race
    for i, runner in enumerate(sorted(male_runners_2024, key=lambda x: x['time_800_pr'] if x['time_800_pr'] is not None else '9999:59:59'), start=1):
        runner['time_800_rank'] = i
    for i, runner in enumerate(sorted(male_runners_2024, key=lambda x: x['time_1600_pr'] if x['time_1600_pr'] is not None else '9999:59:59'), start=1):
        runner['time_1600_rank'] = i
    for i, runner in enumerate(sorted(male_runners_2024, key=lambda x: x['time_3200_pr'] if x['time_3200_pr'] is not None else '9999:59:59'), start=1):
        runner['time_3200_rank'] = i

    # Calculate overall rank as the average of the individual race ranks
    for runner in male_runners_2024:
        runner['overall_rank'] = "{:.2f}".format(sum([runner['time_800_rank'], runner['time_1600_rank'], runner['time_3200_rank']]) / 3)

    # Sort runners by overall rank and assign place rank
    sorted_runners = sorted(male_runners_2024, key=lambda x: x['overall_rank'])
    for i, runner in enumerate(sorted_runners, start=1):
        runner['place_rank'] = i

    return sorted_runners

def get_female_runners_2024():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT runners.first_name, runners.last_name,
                   MIN(case when race_type.race_type_name = '800m' then race_detail.duration_time end) as time_800_pr,
                   MIN(case when race_type.race_type_name = '1600m' then race_detail.duration_time end) as time_1600_pr,
                   MIN(case when race_type.race_type_name = '3200m' then race_detail.duration_time end) as time_3200_pr,
                   MIN(case when race_type.race_type_name = '5k' then race_detail.duration_time end) as time_5k_pr
            FROM runners
            JOIN race_detail ON runners.runner_id = race_detail.runner_id
            JOIN race ON race_detail.race_id = race.race_id
            JOIN race_type ON race_detail.race_type_id = race_type.race_type_id
            WHERE runners.gender = 'Female' AND EXTRACT(YEAR FROM race.race_date) = 2024
            GROUP BY runners.runner_id
        """)
        female_runners_2024 = cur.fetchall()

    # Add ranking in Python for each race
    for i, runner in enumerate(sorted(female_runners_2024, key=lambda x: x['time_800_pr'] if x['time_800_pr'] is not None else '9999:59:59'), start=1):
        runner['time_800_rank'] = i
    for i, runner in enumerate(sorted(female_runners_2024, key=lambda x: x['time_1600_pr'] if x['time_1600_pr'] is not None else '9999:59:59'), start=1):
        runner['time_1600_rank'] = i
    for i, runner in enumerate(sorted(female_runners_2024, key=lambda x: x['time_3200_pr'] if x['time_3200_pr'] is not None else '9999:59:59'), start=1):
        runner['time_3200_rank'] = i

    # Calculate overall rank as the average of the individual race ranks
    for runner in female_runners_2024:
        runner['overall_rank'] = "{:.2f}".format(sum([runner['time_800_rank'], runner['time_1600_rank'], runner['time_3200_rank']]) / 3)

    # Sort runners by overall rank and assign place rank
    sorted_runners = sorted(female_runners_2024, key=lambda x: x['overall_rank'])
    for i, runner in enumerate(sorted_runners, start=1):
        runner['place_rank'] = i

    return sorted_runners