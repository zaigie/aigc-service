import openai
import concurrent.futures
import os
from revChatGPT.Official import Chatbot

defaultModel = "chat-davinci-002-XXXXXXXX"
successfulModels = []


def test_model(model):
    try:
        bot = Chatbot(api_key="...", engine=model)
        response = bot.ask("say this is a test")
        if response:
            successfulModels.append(model)
    except openai.InvalidRequestError:
        print("Model [" + model + "] failed to load. (Invalid Request Error)")


with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    for year in range(2022, 2024):
        for month in range(1, 13):
            for day in range(1, 32):
                formatted_year = "{:04d}".format(year)
                formatted_month = "{:02d}".format(month)
                formatted_day = "{:02d}".format(day)
                model = defaultModel.replace(
                    "XXXXXXXX", formatted_year + formatted_month + formatted_day
                )
                executor.submit(test_model, model)

print("Successful Models: " + str(successfulModels))
