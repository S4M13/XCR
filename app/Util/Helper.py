from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import flash
from flask import current_app

if __name__ == "__main__":
    from ...app import Settings
    import Auth
    from GlobalContext import GlobalContext
    import Database
else:
    import Settings
    from Util import Auth
    from Util.GlobalContext import GlobalContext
    from Util import Database

import functools
from functools import wraps
import datetime
import os
import random


def is_safe_path(basedir: str, path: str, follow_symlinks: bool = True):
    """
    Checks if a given path contains any possible directory traversal attack. It ensures that the path is in the
    given base directory

    :param basedir: The directory in which the path must resolve
    :param path: The path to check
    :param follow_symlinks: Whether symlinks should be follow or not when evaluating the final location
    :return: A bool representing whether the path resolves to within the basedir
    """
    if follow_symlinks:
        return os.path.realpath(path).startswith(basedir)

    return os.path.abspath(path).startswith(basedir)


def request_form(*params, emtpy_invalid: bool = True):
    """
    Securely deals with HTML POST forms and passes along the contents.

    :param params: The names of the input fields
    :param emtpy_invalid: If empty fields should be counted as invalid [Default: True]
    :return: Wrapper function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            param_values = []

            for parameter in params:
                if parameter not in request.form:
                    missing_param = parameter
                    break
                elif (not request.form[parameter]) and emtpy_invalid:
                    missing_param = parameter
                    break
                else:
                    param_values.append(request.form[parameter])
            else:
                return func(*args, *param_values, **kwargs)

            current_app.logger.warning(f"A form was submitted to '{func.__name__}' which was missing the"
                                       f" '{missing_param}' field and was subsequently rejected")
            return "Invalid form"  # TODO : Implement a send back to previous page with error message

        return wrapper

    return inner


def request_args(*params, emtpy_invalid: bool = True):
    """
    Securely deals with HTML GET arguments and passes along the contents.

    :param params: The names of the input fields
    :param emtpy_invalid: If empty fields should be counted as invalid [Default: True]
    :return: Wrapper function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            param_values = []

            for parameter in params:
                if parameter not in request.args:
                    missing_param = parameter
                    break
                elif (not request.args[parameter]) and emtpy_invalid:
                    missing_param = parameter
                    break
                else:
                    param_values.append(request.args[parameter])
            else:
                return func(*args, *param_values, **kwargs)

            current_app.logger.warning(f"A GET request was submitted to '{func.__name__}' which was missing the"
                                       f" '{missing_param}' field and was subsequently rejected")
            return "Invalid form"  # TODO : Implement a send back to previous page with error message

        return wrapper

    return inner


def render_base_template(session: Auth.Session, extension: str, **kwargs) -> str:
    """
    Renders the main page template, with any given extension.

    :param session: The user's session
    :param extension: The extension path
    :param kwargs: Additional keyword arguments to be passed to the renderer
    :return: The rendered HTML template
    """
    current_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    return render_template(extension,
                           session=session,
                           current_date=current_date,
                           version=Settings.CURRENT_VERSION,
                           **kwargs)


def smart_comp(x, y) -> int:
    """
    Performs a smart comparison between two data points of the format ('%W-%Y', data) by comparing the date stamp
    intelligently.

    :param x: Base data point
    :param y: Comparative data point
    :return: Sort compliant integer comparison
    """
    x_dt = datetime.datetime.fromisocalendar(int(x[0].split('-')[1]), int(x[0].split('-')[0]), 1)
    y_dt = datetime.datetime.fromisocalendar(int(y[0].split('-')[1]), int(y[0].split('-')[0]), 1)

    if x_dt > y_dt:
        return 1
    elif x_dt < y_dt:
        return -1
    else:
        return 0


def week_filler_analysis(data: list, default_value=0) -> list:
    """
    Takes a list of sorted tuples containing pairs in the format ('%W-%Y', data). This function will then add any keys which
    are not included from the first date to the current date, inserting the data as the `default_value`

    NOTE: The list must be sorted by the date order of the keys

    :param data: A list containing entries in the format ('%W-%Y', data)
    :param default_value: The value to assign to weeks that are not already in the list
    :return: A list of tuples in the format ('%W-%Y', data)
    """
    date = datetime.date.today()

    if data:
        current_week = int(data[0][0].split("-")[0])
        current_year = int(data[0][0].split("-")[1])

        end_week = int(data[-1][0].split("-")[0])
        end_year = int(data[-1][0].split("-")[1])
    else:
        end_week = 0
        end_year = 0

        current_week = 1
        current_year = date.isocalendar()[0]

    actual_week = date.isocalendar()[1]
    actual_year = date.isocalendar()[0]

    if actual_year > end_year:
        end_week = actual_week
        end_year = actual_year
    elif actual_week > end_week and actual_year == end_year:
        end_week = actual_week

    stamps = []

    while current_week != end_week or current_year != end_year:
        stamps.append(f"{str(current_week).zfill(2)}-{current_year}")
        current_week += 1
        if current_week == datetime.date(current_year, 12, 28).isocalendar()[1] + 1:
            current_week = 1
            current_year += 1

    stamps.append(f"{str(current_week).zfill(2)}-{current_year}")

    current_stamps = [x[0] for x in data]
    appended_data = data

    for date_stamp in stamps:
        if date_stamp not in current_stamps:
            appended_data.append((date_stamp, default_value))

    appended_data.sort(key=functools.cmp_to_key(smart_comp))
    return appended_data


def get_random_color(pastel_factor=0.5):
    return [(x + pastel_factor) / (1.0 + pastel_factor) for x in [random.uniform(0, 1.0) for i in [1, 2, 3]]]


def color_distance(c1, c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])


def generate_new_color(existing_colors, pastel_factor=0.5):
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color


def generate_distinct_colors(number: int, seed: int = 10) -> list:
    """
    This functions generates a number of distinct colors that can be seen to be different by the human eye

    :param number: The number of colors to generate
    :param seed: Defaults to 10, change this in order to change the colors
    :return: A list of distinct colors, each color being a list of RGB values
    """

    random.seed(seed)
    colors = []

    for i in range(number):
        colors.append(generate_new_color(colors, pastel_factor=0.9))

    return [[round(rgb * 255) for rgb in color] for color in colors]


def update_database_analysis():
    """
    Reloads the database analysis statistics to be cached in memory.
    """

    records = Database.Record.query.all()  # Collect all records from the database for analysis
    temp = {}

    # Define all the analysis records
    percentage_attendance_analysis = {}
    percentage_attendance_once_analysis = {}
    percentage_attendance_club_analysis = {}
    club_breakdown_analysis = {}
    weekly_multi_attendance_analysis = {}
    multi_attendance_analysis = {}

    for entry in records:  # Loop all the records and carry out the analysis
        iso_stamp = entry.attendance_date.isocalendar()
        weekly_stamp = f"{str(iso_stamp[1]).zfill(2)}-{iso_stamp[0]}"  # Get the weekly stamp for the record

        # Add the records into the overall attendance records
        if weekly_stamp in percentage_attendance_analysis.keys():
            percentage_attendance_analysis[weekly_stamp] += 1
        else:
            percentage_attendance_analysis[weekly_stamp] = 1

        # Add the records into the attendance records, broken down by club
        if entry.club_uid not in percentage_attendance_club_analysis.keys():
            percentage_attendance_club_analysis[entry.club_uid] = {}

        if weekly_stamp in percentage_attendance_club_analysis[entry.club_uid]:
            percentage_attendance_club_analysis[entry.club_uid][weekly_stamp] += 1
        else:
            percentage_attendance_club_analysis[entry.club_uid][weekly_stamp] = 1

        # Add the records into the club breakdown
        if entry.club_uid in club_breakdown_analysis.keys():
            club_breakdown_analysis[entry.club_uid] += 1
        else:
            club_breakdown_analysis[entry.club_uid] = 1

        # Add the records into the single attendance record, recording which people have already attended in the week
        if weekly_stamp in percentage_attendance_once_analysis.keys():
            if entry.student_uid not in percentage_attendance_once_analysis[weekly_stamp]:
                percentage_attendance_once_analysis[weekly_stamp].append(entry.student_uid)
        else:
            percentage_attendance_once_analysis[weekly_stamp] = [entry.student_uid]

        # Add the records into the weekly multi attendance records
        if weekly_stamp in weekly_multi_attendance_analysis.keys():
            if entry.student_uid in weekly_multi_attendance_analysis[weekly_stamp]:
                weekly_multi_attendance_analysis[weekly_stamp][entry.student_uid] += 1
            else:
                weekly_multi_attendance_analysis[weekly_stamp][entry.student_uid] = 1
        else:
            weekly_multi_attendance_analysis[weekly_stamp] = {entry.student_uid: 1}

        # Add the records into the multi attendance records
        if entry.student_uid in multi_attendance_analysis.keys():
            if entry.club_uid not in multi_attendance_analysis[entry.student_uid]:
                multi_attendance_analysis[entry.student_uid].append(entry.club_uid)
        else:
            multi_attendance_analysis[entry.student_uid] = [entry.club_uid]

    #  Collect general data about datastore in order to make comparisons
    NUMBER_OF_STUDENTS = len(GlobalContext.STUDENTS_DATASTORE.data)
    TOTAL_ATTENDANCES = len(records)

    # Complete analysis and reformat data

    # Format percentage_attendance_analysis
    percentage_attendance_analysis = list(percentage_attendance_analysis.items())
    percentage_attendance_analysis.sort(key=functools.cmp_to_key(smart_comp))

    for index, entry in enumerate(percentage_attendance_analysis):
        percentage_attendance_analysis[index] = (entry[0], round((entry[1] / NUMBER_OF_STUDENTS) * 100, 2))

    percentage_attendance_analysis = week_filler_analysis(percentage_attendance_analysis)

    # Format percentage_attendance_club_analysis
    for key, club_data in percentage_attendance_club_analysis.items():
        percentage_attendance_club_analysis[key] = list((percentage_attendance_club_analysis[key].items()))
        percentage_attendance_club_analysis[key].sort(key=functools.cmp_to_key(smart_comp))

        for index, entry in enumerate(percentage_attendance_club_analysis[key]):
            percentage_attendance_club_analysis[key][index] = (entry[0],
                                                               round((entry[1] / NUMBER_OF_STUDENTS) * 100, 2))

        percentage_attendance_club_analysis[key] = week_filler_analysis(percentage_attendance_club_analysis[key])

    # Format club_breakdown_analysis
    for club_uid, data in club_breakdown_analysis.items():
        club_breakdown_analysis[club_uid] = round((data / TOTAL_ATTENDANCES) * 100, 2)

    # Format percentage_attendance_once_analysis
    for weekly_stamp, weekly_entry in percentage_attendance_once_analysis.items():
        percentage_attendance_once_analysis[weekly_stamp] = len(percentage_attendance_once_analysis[weekly_stamp])

    percentage_attendance_once_analysis = list(percentage_attendance_once_analysis.items())
    percentage_attendance_once_analysis.sort(key=functools.cmp_to_key(smart_comp))

    for index, entry in enumerate(percentage_attendance_once_analysis):
        percentage_attendance_once_analysis[index] = (entry[0], round((entry[1] / NUMBER_OF_STUDENTS) * 100, 2))

    percentage_attendance_once_analysis = week_filler_analysis(percentage_attendance_once_analysis)

    # Format weekly_multi_attendance_analysis
    weekly_multi_attendance_analysis = list(weekly_multi_attendance_analysis.items())
    weekly_multi_attendance_analysis.sort(key=functools.cmp_to_key(smart_comp))

    weekly_multi_attendance_analysis = week_filler_analysis(weekly_multi_attendance_analysis, default_value = {})

    percentage_attendance_twice_analysis = []
    percentage_attendance_thrice_analysis = []

    for data in weekly_multi_attendance_analysis:
        twice_count = 0
        thrice_count = 0

        for value in data[1].values():
            if value >= 2:
                twice_count += 1

            if value >= 3:
                thrice_count += 1

        percentage_attendance_twice_analysis.append((data[0], twice_count))
        percentage_attendance_thrice_analysis.append((data[0], thrice_count))

    for index, entry in enumerate(percentage_attendance_twice_analysis):
        percentage_attendance_twice_analysis[index] = (entry[0], round((entry[1] / NUMBER_OF_STUDENTS) * 100, 2))

    for index, entry in enumerate(percentage_attendance_thrice_analysis):
        percentage_attendance_thrice_analysis[index] = (entry[0], round((entry[1] / NUMBER_OF_STUDENTS) * 100, 2))

    # Format multi_attendance_analysis
    attended_one_count = 0
    attended_three_count = 0
    attended_five_count = 0

    for student_uid, clubs in multi_attendance_analysis.items():
        multi_attendance_analysis[student_uid] = len(clubs)

    for value in multi_attendance_analysis.values():
        if value >= 1:
            attended_one_count += 1
        if value >= 3:
            attended_three_count += 1
        if value >= 5:
            attended_five_count += 1

    attended_one_count = round((attended_one_count / NUMBER_OF_STUDENTS) * 100, 2)
    attended_three_count = round((attended_three_count / NUMBER_OF_STUDENTS) * 100, 2)
    attended_five_count = round((attended_five_count / NUMBER_OF_STUDENTS) * 100, 2)

    # Format results into JSON format and save into memory

    percentage_attendance_analysis_formatting = {}
    percentage_attendance_analysis_formatting["success"] = True
    percentage_attendance_analysis_formatting["labels"] = [entry[0] for entry in percentage_attendance_analysis]
    percentage_attendance_analysis_formatting["datasets"] = [
        {"label": "Weekly % Attendance",
         "backgroundColor": "rgb(255, 99, 132)",
         "borderColor": "rgb(255, 99, 132)",
         "data": [entry[1] for entry in percentage_attendance_analysis],
         "fill": False
         }
    ]

    temp["overall_weekly_attendance"] = percentage_attendance_analysis_formatting

    percentage_attendance_club_analysis_formatting = {}
    percentage_attendance_club_analysis_formatting["success"] = True
    percentage_attendance_club_analysis_formatting["labels"] = [entry[0] for entry in percentage_attendance_analysis]
    percentage_attendance_club_analysis_formatting["datasets"] = []

    colors = generate_distinct_colors(len(percentage_attendance_club_analysis.items()))

    for club_uid, dataset, color in zip(percentage_attendance_club_analysis.keys(),
                                        percentage_attendance_club_analysis.values(),
                                        colors):
        club_name = GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_uid)[0][1]

        percentage_attendance_club_analysis_formatting["datasets"].append(
            {"label": f"Weekly % Attendance for {club_name}",
             "backgroundColor": f"rgb({color[0]}, {color[1]}, {color[2]})",
             "borderColor": f"rgb({color[0]}, {color[1]}, {color[2]})",
             "data": [entry[1] for entry in dataset],
             "fill": False
             }
        )

    temp["overall_weekly_attendance_by_club"] = percentage_attendance_club_analysis_formatting

    club_breakdown_analysis_formatting = {}
    club_breakdown_analysis_formatting["success"] = True
    club_breakdown_analysis_formatting["labels"] = [
        GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_uid)[0][1]
        for club_uid in club_breakdown_analysis.keys()
    ]

    club_breakdown_analysis_formatting["datasets"] = [
        {"label": "% of total attendance",
         "backgroundColor": ['#%02x%02x%02x' % (color[0], color[1], color[2])
                             for color in generate_distinct_colors(len(club_breakdown_analysis.items()))],
         "data": [data for data in club_breakdown_analysis.values()]
         }
    ]

    temp["club_breakdown"] = club_breakdown_analysis_formatting

    percentage_attendance_once_analysis_formatting = {}
    percentage_attendance_once_analysis_formatting["success"] = True
    percentage_attendance_once_analysis_formatting["labels"] = [entry[0] for entry in percentage_attendance_once_analysis]
    percentage_attendance_once_analysis_formatting["datasets"] = [
        {"label": "Weekly % Attendance of one club or more",
         "backgroundColor": "rgb(12, 255, 132)",
         "borderColor": "rgb(12, 255, 132)",
         "data": [entry[1] for entry in percentage_attendance_once_analysis],
         "fill": False
         },
        {"label": "Weekly % Attendance of two clubs or more",
         "backgroundColor": "rgb(255, 12, 132)",
         "borderColor": "rgb(255, 12, 132)",
         "data": [entry[1] for entry in percentage_attendance_twice_analysis],
         "fill": False
         },
        {"label": "Weekly % Attendance of three clubs or more",
         "backgroundColor": "rgb(12, 255, 12)",
         "borderColor": "rgb(12, 255, 12)",
         "data": [entry[1] for entry in percentage_attendance_thrice_analysis],
         "fill": False
         }
    ]

    temp["overall_weekly_attendance_once"] = percentage_attendance_once_analysis_formatting

    flash_cards = {
        "success": True,
        "one": attended_one_count,
        "three": attended_three_count,
        "five": attended_five_count
    }

    temp["flash_cards"] = flash_cards

    GlobalContext.DATABASE_ANALYSIS = temp
