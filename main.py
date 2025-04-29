import telebot
from telebot import types, TeleBot
import requests

bot = telebot.TeleBot('7939528904:AAElGRlo7zCIwcFgF0QENiGhYheFwN_l3L0') #TG Bot


# Getting weather
w_api = "97ca2d07d3474bc5b2700224252904"
cities = ["berlin", "london", "paris", "tokyo", "astana", "almaty"]  #List of cities that can be used

# Repair solutions database
rep_list = {
    "shifter": "If the chain makes noise when it is on certain gear, then rotate the barrel tensioner - clockwise to tension the cable, counterclockwise to loosen it.",
    "wheels": "Make sure that all of your bolts are sufficiently tighened. If the problem still persists, then see if an axle might have been broken. For that, you need to disassemble the back wheel and take the axle out",
    "brakes": "If your brakes are too loose, then unscrew the bolt holding the cable at the brake pad, tension the cable and rescrew the bolt back in. If brake is making noise, then unscrew bolts that hold the brakes to the wheels, align the brakes, and retighten them. If it's partially making noise then you need to bend the brake disc with pliers",
}


# The Logic
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_weather = types.KeyboardButton('Weather')
    btn_repair = types.KeyboardButton('Repair')

    markup.row(btn_weather, btn_repair)

    bot.send_message(message.chat.id, 'Hello! This is Bike Repair Bot, made to answer questions regarding repairs!\n'
                                      'Choose an option:\n'
                                      '/weather: Displays current weather in cities and gives recommendations based on that\n'
                                      '/repair: Gives advice on how to repair your bike!', reply_markup=markup)
    bot.register_next_step_handler(message, main_choice)

#Handling choice of user

def main_choice(message):
    if message.text == "Weather":
        cityname(message)
    elif message.text == "Repair":
        repair_menu(message)
    else:
        # Invalid input - show main menu again
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_weather = types.KeyboardButton('Weather')
        btn_repair = types.KeyboardButton('Repair')
        markup.row(btn_weather, btn_repair)

        bot.send_message(message.chat.id, 'Please use the buttons:', reply_markup=markup)
        bot.register_next_step_handler(message, main_choice)


# Weather Function
def cityname(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = types.KeyboardButton('Back')
    markup.add(btn_back)

    bot.send_message(message.chat.id, "Enter your city name (e.g., Berlin):", reply_markup=markup)
    bot.register_next_step_handler(message, handle_city)


def handle_city(message):
    if message.text.lower() == "back":
        return main(message)

    city = message.text.strip().lower()
    if city not in cities: #if city is unrecognised
        bot.send_message(message.chat.id, "City not in our database. Try again:")
        bot.register_next_step_handler(message, handle_city)
        return

    weather_data = get_weather(city)
    if not weather_data: #if api fails
        bot.send_message(message.chat.id, "Weather service unavailable. Try again later:")
        bot.register_next_step_handler(message, handle_city)
        return

    response = (
        f"Weather in {city.title()}:\n"
        f"• Temperature: {weather_data['temp']}°C\n"
        f"• Wind: {weather_data['wind']} km/h\n"
        f"• Rain: {weather_data['rain']} mm\n"
        f"• Humidity: {weather_data['humidity']}%\n"
        f"• Conditions: {weather_data['condition']}\n\n"
    )

    # Fetch weather data
    weather_data = get_weather(city)
    if not weather_data:
        bot.send_message(message.chat.id, "Failed to fetch weather. Try another city:")
        bot.register_next_step_handler(message, handle_city)
        return

    # Advice depending on conditions
    if weather_data["wind"] > 20:
        response += "Strong winds! Might not be worth it to cycle."
    if weather_data["rain"] > 3:
        response += "Make sure to be careful"

    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, handle_city)  # Loop back


def get_weather(city): #Getting Weather Data

    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={w_api}&q={city}&aqi=no"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            print(f"WeatherAPI Error: {data['error']['message']}")
            return None

        return {
            "temp": data["current"]["temp_c"],
            "wind": data["current"]["wind_kph"],
            "rain": data["current"]["precip_mm"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"]
        }
    except Exception as e:
        print(f"API Request Failed: {e}")
        return None


# The Repair Page
def repair_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_shifter = types.KeyboardButton('Shifter')
    btn_wheels = types.KeyboardButton('Wheels')
    btn_brakes = types.KeyboardButton('Brakes')
    btn_back = types.KeyboardButton('Back')

    markup.row(btn_shifter, btn_wheels)
    markup.row(btn_brakes, btn_back)

    bot.send_message(message.chat.id, "Select a repair category:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_repair_choice)

#Logic of Repair Page

def handle_repair_choice(message):
    if message.text == "Back":
        return main(message)

    choice = message.text.lower()
    if choice not in rep_list:
        bot.send_message(message.chat.id, "Invalid option. Please use buttons:")
        bot.register_next_step_handler(message, handle_repair_choice)
        return

    # Send repair solution
    bot.send_message(message.chat.id, rep_list[choice])

    # Show repair menu again (loop)
    repair_menu(message)


#Bot doesn't stop
bot.polling(none_stop=True)
