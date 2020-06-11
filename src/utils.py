import re
from time import strptime
from datetime import date
import pandas as pd


def room_dict_to_df(room_dict):

    # Initialize dataframe containing all listings
    df = pd.DataFrame()

    # Convert dict of formate {date: [rooms]} to dataframe where every row
    # is a room with house, room_number and move-in date
    for date, rooms in room_dict.items():
        for room_id in rooms:
            house = room_id.split(' ')[0]
            room_number = room_id.split(' ', 1)[1]

            df = df.append(dict(house=house,
                                room_number=room_number,
                                date=date),
                           ignore_index=True)
    return df


def listings_to_string(listings):
    """
    Convert the pandas dataframe of listings to a messageable string.
    """
    message = ""
    dates = []
    for idx in listings.index:

        if listings['date'][idx] not in dates:
            message += f"*\n{listings['date'][idx]}\n*"
            message += "------------\n"
            dates.append(listings['date'][idx])
        message += f"{listings['house'][idx]} {listings['room_number'][idx]}\n"
    if not message:
        message = "empty"
    return message


def convert_list_to_message(list):
    message = ""
    for item in list:
        message += str(item) + " \n"
    return message


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def convert_string_to_date(date_string):
    """
    Converts string in the format 01July2019 to datetime format

    Args:
        string date_string: Date as string

    Returns:
        date date_formated: Date as formated in datetime library

    """
    month_string = " ".join(re.findall("[a-zA-Z]+", date_string))
    day, year = date_string.split(month_string)
    print(day)
    print(year)
    month_num = strptime(month_string[0:3],'%b').tm_mon
    print(month_num)
    date_formated = date(int(year), month_num, int(day))
    
    return date_formated
    
    
    
    
    
