
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
import logging
import re
from time import sleep, localtime
from random import randint
from threading import Thread
import fmel
import utils
from datetime import date, timedelta

import pandas as pd
import configparser

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class FMELBot:
    """
    Implements the Telegram interface of the FMEL scraper.
    Listings are scraped regularly and stored in a Pandas Dataframe
    Save the Dataframe to disk as a csv-file.
    """
    def __init__(self, ):

        # Read necessary parameters from config file
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.username = config['FMEL']['username']
        self.password = config['FMEL']['password']
        TOKEN = config['TelegramBot']['token']

        self.fmel_scraper = fmel.FMELScraper()
        self.init_bot(TOKEN)
        #self.updater, self.dispatcher = self.init_bot(TOKEN)

        columns = ['date', 'room']
        self.listings = pd.DataFrame(columns=columns)

    def start(self, update, context):
        update.message.reply_text('Welcome to the super-secret FMEL Bot!')
        # We need to initialize all relevant user_data here
        buttons = [
            InlineKeyboardButton("Atrium", callback_data="Atrium"),
            InlineKeyboardButton("Azur", callback_data="Azur"),
            InlineKeyboardButton("Bourdo", callback_data="Bourdonnette"),
            InlineKeyboardButton("Cèdres", callback_data="Cèdres"),
            InlineKeyboardButton("Colline", callback_data="Colline"),
            InlineKeyboardButton("Falaises", callback_data="Falaises"),
            InlineKeyboardButton("Jordils", callback_data="Jordils"),
            InlineKeyboardButton("Marcolet", callback_data="Marcolet"),
            InlineKeyboardButton("Ochettes", callback_data="Ochettes"),
            InlineKeyboardButton("Rainbow", callback_data="Rainbow"),
            InlineKeyboardButton("Rhodanie", callback_data="Rhodanie"),
            InlineKeyboardButton("Triaudes", callback_data="Triaudes"),
            InlineKeyboardButton("Square", callback_data="Square"),
            InlineKeyboardButton("Yverdon", callback_data="Yverdon"),
            InlineKeyboardButton("Zenith", callback_data="Zenith")
        ]

        context.user_data['buttons'] = buttons
        context.user_data['selected_houses'] = []
        context.user_data['notifications'] = False

    def print_context(self, update, context):
        update.message.reply_text(context.user_data['selected_houses'])

    def init_bot(self, TOKEN):
        """
        Initializes the telegram bot and returns an updater and dispatcher.
        """
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # Add handlers for special commands, e.g. "/start"
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('select_houses', self.select_houses))
        dispatcher.add_handler(CommandHandler('update_listings', self.update_listings))
        dispatcher.add_handler(CommandHandler('show_listings', self.show_listings))
        dispatcher.add_handler(CommandHandler('print_context', self.print_context))

        # Add handler for button menu for house selection
        dispatcher.add_handler(CallbackQueryHandler(self.button)),

        updater.start_polling()
        updater.idle()

        #return updater, dispatcher

    def update_listings(self, update, context):
        """
        Fetches the current listings from the FMEL site and stores them to self.listings
        """
        # Login to FMEL
        self.fmel_scraper.login(self.username, self.password)
        sleep(2)

        # Scrape all the latest entries
        room_dict = self.fmel_scraper.get_listings()
        self.listings = utils.room_dict_to_df(room_dict)

    def show_listings(self, update, context):

        """
        Messages the latest saved listings that match the users settings.
        """

        # Filter the listings according to selected preferences
        # If no house selection was made, all listings are returned.
        if context.user_data['selected_houses']:
            filtered_listings = self.listings[self.listings['house'].isin(context.user_data['selected_houses'])]
        else:
            filtered_listings = self.listings

        message = utils.listings_to_string(filtered_listings)
        update.message.reply_text(message)

    def button(self, update, context):
        """
        Handles the pressed buttons with houses that should go on the watchlist. Adds the according house to the
        watchlist and adds a check mark to the button symbol in the bot.
        
        First reads the callback data (i.e. the information on the pressed button).
        Then iterates over all existing buttons to find the corresponding button instance.
        Checks, if the corresponding house is already on the list of selected houses checks/unchecks it from that 
        list accordingly.

        Args:
            update:
            context:

        Returns:

        """
        selected_option = update.callback_query.data # Read the callback data that was received
        
        for i, button in enumerate(context.user_data['buttons']):
            if selected_option == button.callback_data: # Check what button the input came frome
                # Check if house is already on the list, i.e. if it should be checked in or checked out
                if button.callback_data not in context.user_data['selected_houses']:

                    # Add a checkmark to that button
                    context.user_data['buttons'][i] = InlineKeyboardButton(button.text + " ✔",
                                                                           callback_data=button.callback_data)
                    context.user_data['selected_houses'].append(button.callback_data)
                else:
                    context.user_data['buttons'][i] = InlineKeyboardButton(re.sub(" ✔", " ", button.text),
                                                                           callback_data=button.callback_data)
                    context.user_data['selected_houses'].remove(button.callback_data)
                reply_markup = InlineKeyboardMarkup(utils.build_menu(context.user_data['buttons'],
                                                                    n_cols=2))
                context.bot.editMessageReplyMarkup(chat_id=update.effective_message.chat_id,
                                                   message_id=update.effective_message.message_id,
                                                   reply_markup=reply_markup)

    def select_houses(self, update, context):
        """
        Opens a Keyboard markup that lets you select the houses that you wanna track. 

        Args:
            update:
            context:

        Returns:

        """
        reply_markup = InlineKeyboardMarkup(utils.build_menu(context.user_data['buttons'],
                                                             n_cols=2))
        update.message.reply_text("Choose the house you want to receive updates about", reply_markup=reply_markup)


    # def timed_updates(self, update, context):
    #     """
    #     Fetches listings in regular intervals by calling self.update_listings which updates self.listings.
    #     To avoid too regular polling of the FMEL server, time update intervals are randomized.
    #     (Update intervals might as well be set to a fixed value but I am paranoid about this.)
    #     Update intervals are changed according to the time of the day.
    #
    #     There is only one instance of this function running, providing updates for all users!
    #
    #     Args:
    #         update:
    #         context:
    #
    #     Returns:
    #
    #     """
    #
    #     mean_ui_day = 1200 # mean update interval day
    #     mean_ui_night = 10800 # mean update interval night
    #
    #     while True:
    #         self.update_listings(update, context)
    #
    #         mytime = localtime()
    #         if 6 < mytime.tm_hour < 22:
    #             print("It's is daytime meine dudes")
    #             sleep(randint(mean_ui_day*0.8, mean_ui_day*1.2))
    #         else:
    #             print("It's is nighttime meine dudes")
    #             sleep(randint(mean_ui_night*0.8, mean_ui_night*1.2))
    #
    # def timed_notifications(self, update, context):
    #     """
    #     Sends a message to the user if a new room has been published in a house on the list of selected houses.
    #     Does not conduct listings update on its own but instead relies on regular updates by self.timed_updates
    #
    #     There is one instance of this function running per user that used the /notify_me command. All instances
    #     have their own thread.
    #
    #     Args:
    #         update:
    #         context:
    #
    #     Returns:
    #
    #     """
    #     daily_timer = 0
    #     update_interval = 1200
    #     while True:
    #         # Save listings that had previously been saved for this user
    #         old_listings = context.user_data['filtered_listings']
    #         # Fetch the up-to-date listings and filter them according to the wishes of the user
    #         new_listings = self.filter_listings(update, context)
    #
    #         # Check if a new date for move-in is available
    #         # Find dates that are in the new_listings but not in the old listings
    #         new_date = False
    #         diff_dates = list(new_listings.keys() - old_listings.keys())
    #         for diff_date in diff_dates:
    #             for new_date in new_listings.keys():
    #                 if diff_date - new_date > timedelta(days=2):
    #                     new_date = True
    #         if new_date:
    #             update.message.reply_text("A new date is available for booking!")
    #
    #         # Check if a new room has been published for any of the dates
    #         old_rooms = set()
    #         new_rooms = set()
    #         for date in new_listings.keys():
    #             for room in new_listings[date]:
    #                 new_rooms.add(room)
    #         for date in old_listings.keys():
    #             for room in old_listings[date]:
    #                 old_rooms.add(room)
    #
    #         booked_rooms = list(old_rooms - new_rooms)
    #         published_rooms = list(new_rooms - old_rooms)
    #
    #         if published_rooms:
    #             update.message.reply_text("One or more new rooms have been published: \n")
    #             message = utils.convert_list_to_message(published_rooms)
    #             update.message.reply_text(message)
    #         if booked_rooms:
    #             update.message.reply_text("The following room was just booked: \n")
    #             message = utils.convert_list_to_message(booked_rooms)
    #             update.message.reply_text(message)
    #
    #         daily_timer = daily_timer + update_interval
    #         if daily_timer > 86400:
    #             update.message.reply_text("Bot is still alive")
    #             message = utils.convert_listings_to_string(new_listings)
    #             update.message.reply_text(message)
    #             daily_timer = 0
    #         #if not booked_rooms and not published_rooms:
    #         #    update.message.reply_text("Nothing changed")
    #         # FOR NOW
    #         #message = utils.convert_listings_to_string(new_listings)
    #         #update.message.reply_text(message)
    #         sleep(update_interval)
    #
    # def notify_me(self, update, context):
    #     if context.user_data['notifications']:
    #         update.message.reply_text('Notifications are already on')
    #     else:
    #         update.message.reply_text('Bot checks FMEL webpage for new listings every 20 minutes and sends you a message'
    #                                   'as soon as a new listing among your selected houses is up. This function will also'
    #                                    ' send you a keep-alive message every 24 hours')
    #         notif_thread = Thread(target=self.timed_notifications, args=(update, context,))
    #         notif_thread.setDaemon(True)
    #         notif_thread.start()
    #         context.user_data['notifications'] = True
    #
    #     if not self.updates:
    #         update_thread = Thread(target=self.timed_updates, args=(update, context,))
    #         update_thread.setDaemon(True)
    #         update_thread.start()
    #         self.updates = True


if __name__ == "__main__":
    bot = FMELBot()
