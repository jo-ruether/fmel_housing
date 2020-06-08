import re
from time import strptime
from datetime import date


def convert_listings_to_string(listings):
    message = ""
    for date, domiciles in listings.items():
        message += str(date) + "\n"
        for domicile in domiciles:
            message += " \ " + str(domicile) + "\n"
        message += "\n"
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
    
    
    
    
    
