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
    return render_template('results.html',
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
        cur.execute("SELECT roster_id FROM rosters WHERE gender = %s ORDER BY roster_year DESC LIMIT 1", (gender,))
        roster_id = cur.fetchone()['roster_id']

        sql = f"""
            SELECT runner_id, grad_year, {distance}, first_name, last_name,
            ROW_NUMBER() OVER (ORDER BY {distance} ASC) as runner_ranking
            FROM runners
            WHERE gender = %s AND {distance} > 0
            ORDER BY {distance} ASC
            LIMIT 10
        """
        cur.execute(sql, (gender,))
        best_runners = cur.fetchall()

        cur.execute("SELECT * from ROSTER_DETAIL WHERE roster_id = %s", (roster_id,))
        roster_detail = cur.fetchall()

    # Convert roster_detail to a set for faster lookup
    roster_detail_set = set(row['runner_id'] for row in roster_detail)

    # Add 'is_in_latest_roster' key to each runner in male_runners_800
    for runner in best_runners:
        runner['is_in_latest_roster'] = 1 if runner['runner_id'] in roster_detail_set else 0

    return best_runners

def this_season_best_runners(gender, distance):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT roster_id FROM rosters WHERE gender = %s ORDER BY roster_year DESC LIMIT 1", (gender,))
        roster_id = cur.fetchone()['roster_id']

        sql = f"""
            SELECT runners.runner_id, grad_year, {distance}, first_name, last_name,
            ROW_NUMBER() OVER (ORDER BY {distance} ASC) as runner_ranking
            FROM runners
            JOIN roster_detail ON runners.runner_id = roster_detail.runner_id
            WHERE gender = %s AND {distance} > 0 AND roster_detail.roster_id = %s
            ORDER BY {distance} ASC
        """
        cur.execute(sql, (gender, roster_id))
        best_runners = cur.fetchall()

        cur.execute("SELECT * from ROSTER_DETAIL WHERE roster_id = %s", (roster_id,))
        roster_detail = cur.fetchall()

    # Convert roster_detail to a set for faster lookup
    roster_detail_set = set(row['runner_id'] for row in roster_detail)

    # Add 'is_in_latest_roster' key to each runner in male_runners_800
    for runner in best_runners:
        runner['is_in_latest_roster'] = 1 if runner['runner_id'] in roster_detail_set else 0

    return best_runners