from settings import *

import csv
import json
import re

from dialog import Dialog

from distances import Point,find_closest_walkable, dijkstra_distance,mark_positions,place_characters,find_closest_room_center

import openai

import re

openai.api_key = API_KEY
import csv



def place_tile( X, Y, Tile, rooms,filepath="map/Floor_1/map_1_Collisions.csv",filepath_to_modify="map/Floor_1/map_1_Interactions.csv"):
    print("function called with :", X,Y,Tile)
    
    
    # Read the csv file into a list of lists
    with open(filepath_to_modify, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    for i in range(len(X)):
        try:
            x_val = int(X[i])
            y_val = int(Y[i])
            tile_val = int(Tile[i])
            start = Point(x_val,y_val)
            
            closest_walkable = find_closest_room_center(start, rooms)
            final_x=closest_walkable.x
            final_y=closest_walkable.y
            # Place the tile value at the specified location
            data[final_y][final_x] = tile_val

        except:
            print("OUPS, the model returned some bullshit for index: ", i)
            continue  # Skip to next iteration if there's an error

        

    # Save the list of lists back to the csv file
    with open(filepath_to_modify, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def Create_story_LLM(story,size,genre):

    system_msg = {"role": "system", "content": f'You an AI designed to help me build an interesting game based on a dungeon inside the tower in this story {story}. /n The map is a {size}x{size} tilemap of a {genre} game'}
    
     # Initialize messages array
    messages = [system_msg]
    message=f"with ONLY those available tiles : {AVAILABLE_TILES}, create a basic plot for the level. the story should be less than 100 words long."

    messages.append({"role": "user", "content": message})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
           
)
        # Extract the assistant's message from the response
        # Extract the assistant's message from the response
        assistant_msg = response['choices'][0]['message']

        # Print the model's response
        print('Story: ', assistant_msg.content)
        return assistant_msg.content
    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return

def Create_Level_objective_LLM(level_story,size,genre):
   
    system_msg = {"role": "system", "content": f'You an AI designed to help me build an interesting game based oon a dungeon inside the tower in this story {STORY}. /n The map is a {size}x{size} tilemap of a {genre} game'}
    
     # Initialize messages array
    messages = [system_msg]
    message=f"with ONLY those available tiles : {AVAILABLE_TILES}, and this {level_story} in less than 30 words, provide a 'clear condition' for the level. The portal will only activate if the condition is fullfilled, so make it something feasable. example : 'defeat at least N enemies.' Or ' loot at least N treasur chest ' or ' deafeat the boss and escape'  "

    messages.append({"role": "user", "content": message})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=[
    {
        "name": "set_level_objective",
        "description": "Set a a clear condition for the current level.",
        "parameters": {
            "type": "object",
            "properties": {
                "story": {
                    "type": "string",
                    "description": "A good objective that is feasible on the current level",
                },
              
            },
            "required": ["story"],
        },
    }
        ],
        function_call={"name": "set_level_objective"},
)
        # Extract the assistant's message from the response
        # Extract the assistant's message from the response
        assistant_msg = response['choices'][0]['message']
        response_options = assistant_msg.to_dict()['function_call']['arguments']
        options = json.loads(response_options)


        # Print the model's response
        print('objective: ',options["story"])
        return options["story"]
    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return


def place_LLM_tiles(Level_story,player_pos,boss_pos, boss_name,size,genre,level,rooms,objective):


    system_msg = {"role": "system", "content": f'You an AI designed to help me build an interesting game out of the available assets /n The map is a {size}x{size} tilemap of a {genre} game'}
     
   
    # Initialize messages array
    messages = [system_msg]
    message=f"with ONLY those available tiles : {AVAILABLE_TILES}, create a placement for the tiles as (x,y) coordinates on the map to follow the following story {Level_story} considering that the player starting position is ({player_pos.x},{player_pos.y}) and the boss({boss_name}) position is boss_position ({boss_pos.x},{boss_pos.y})  "
    print(message)
    messages.append({"role": "user", "content": message})
    

    # Create a dataset using GPT-4
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions = [
                {
                    "name": "place_tile",
                    "description": f"Place the tiles on the map at pos (x,y) by iterrating over the give arrays, the X, and Y values can't be greater than the size of the map. There must ALWAYS be one exit portal and not more than 2.Also, the objective must ABSOLUTLY be feasible :{objective}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "X": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "An individual x position for a tile"
                            },
                            "description": f"List of X pos to place the objects on the map. values can't exceed {size}"
                        },
                        "Y": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "An individual y position for a tile"
                            },
                            "description": f"List of Y pos to place the objects on the map values can't exceed {size}"
                        }, 
                        "Tiles": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "An individual Tile value"
                            },
                            "description": "List of Tiles numbers to place the objects on the map"
                        },
                        },
                        "required": ["X","Y","Tiles"],
                    },
                }
            ],
            function_call={"name": "place_tile"},
        )
        
        # Extract the assistant's message from the response
        # Extract the assistant's message from the response
        assistant_msg = response['choices'][0]['message']

        # Print the model's response
        print('NPC: ', assistant_msg)

        # Step 2: check if GPT wanted to call a function
        if assistant_msg.get("function_call"):
            print("calling function")
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "place_tile": place_tile,
            }  # only one function in this example, but you can have multiple
            function_name = assistant_msg["function_call"]["name"]
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(assistant_msg["function_call"]["arguments"])
            print(function_args)
            fuction_to_call(
                X=function_args.get("X"),
                Y=function_args.get("Y"),
                Tile=function_args.get("Tiles"),
                filepath=f"map/Floor_{level}/map_{level}_Collisions.csv",
                filepath_to_modify=f"map/Floor_{level}/map_{level}_Interactions.csv",
                rooms=rooms
            )
    
    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        
def set_LLM_Mood(sentence):
   
    system_msg = {"role": "system", "content": f'You an AI designed to help me answer to some message with the correct tone.'}
    
     # Initialize messages array
    messages = [system_msg]
    message=f"Find the correct tone to answer this : {sentence}"

    messages.append({"role": "user", "content": message})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=[
    {
        "name": "set_mood",
        "description": "Set the mood of the NPC to which the sentence was said.",
        "parameters": {
            "type": "object",
            "properties": {
                "mood": {
                    "type": "string",
                    "description": "A mood between : Neutral , Happy , Sad , Angry or Dull",
                },
              
            },
            "required": ["mood"],
        },
    }
        ],
        function_call={"name": "set_mood"},
)
      # Extract the assistant's message from the response
        # Extract the assistant's message from the response
        assistant_msg = response['choices'][0]['message']
        response_options = assistant_msg.to_dict()['function_call']['arguments']
        options = json.loads(response_options)


        # Print the model's response
        print('Mood: ',options["mood"])
        return options["mood"]
    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return

def answer_with_mood_LLM(player_input,messages,mood):
        # Append the user's message to the messages
    try:

            # Create a dataset using GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=messages,
                functions=[
                    {
                        "name": "get_varied_personality_responses",
                        "description": "ingest the various personality responses",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                f"{mood}": {
                                    "type": "string",
                                    "description": f"A {mood} version of the response to a user's query",
                                },
                                
                            },
                            "required": ["{mood}"],
                        },
                    }
                        ],
                        function_call={"name": "get_varied_personality_responses"},
                )

            reply_content = response.choices[0].message
            response_options = reply_content.to_dict()['function_call']['arguments']
            options = json.loads(response_options)
            moody_answer=options[f"{mood}"]

            # Print the model's response
            print('NPC: ', moody_answer)

            # Append the assistant's message to the messages
            
            return moody_answer
    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return

    
        


def function_call_create_item(rate): 
    try:
        system_intel = "You are an assistent designed to help me build interesting enemies."
        prompt =f"Create an item corresponding to the following rate: {rate}"
        result = openai.ChatCompletion.create(model="gpt-4-0613",
                                    messages=[{"role": "system", "content": system_intel},
                                            {"role": "user", "content": prompt}],
                                            functions=[
                {
                    "name": "create_character_json",
                    "description": "Create a characte given certain characteristics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "the name of the object in less than 5 words.",
                            },
                            "description": {
                                "type": "string",
                                "description": "the description of the object in less than 15 words.",
                            },
                            "item_type": {
                                "type": "string",
                                "description": "the type of the object, between 'weapon','headset','torso','legs','boots','jewel'",
                            },
                            "health_bonus": {
                                "type": "string",
                                "description": "the health bonus that the created item gives between 0 and 20 ",
                            },
                            "enegy_bonus": {
                                "type": "string",
                                "description": "the energy bonus that the created item gives between 0 and 20 ",
                            },
                            "magic_bonus": {
                                "type": "string",
                                "description": "the magic value of the created item between 0 and 10 ",
                            },
                            "strength_bonus": {
                                "type": "string",
                                "description": "the strength value of the created characted between 0 and 10 ",
                            },
                            "speed_bonus": {
                                "type": "string",
                                "description": "the speed value of the created characted between 0 and 0.5 ",
                            },
                        },
                        "required": ["name","description", "item_type", "health_bonus","enegy_bonus","magic_bonus", "strength_bonus", "speed_bonus"],
                    },
                }
            ],
            function_call={"name":"create_character_json"},
        )
        
    
        message = result["choices"][0]["message"]
        print(message)
        response_option=message.to_dict()['function_call']['arguments']   
        print(response_option)
        options=json.loads(response_option)
        return options

    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return
    
def function_call_create_item_from_NPC(rate, prefered_items): 
    try:
        system_intel = "You are an assistent designed to help me build interesting enemies."
        prompt =f"Create an item corresponding to the following rate: {rate}. Gicen your status, you have a tendency to create more {prefered_items}"
        result = openai.ChatCompletion.create(model="gpt-4-0613",
                                    messages=[{"role": "system", "content": system_intel},
                                            {"role": "user", "content": prompt}],
                                            functions=[
                {
                    "name": "create_character_json",
                    "description": "Create a characte given certain characteristics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "the name of the object in less than 5 words.",
                            },
                            "description": {
                                "type": "string",
                                "description": "the description of the object in less than 15 words.",
                            },
                            "item_type": {
                                "type": "string",
                                "description": "the type of the object, between 'weapon','headset','torso','legs','boots','jewel'",
                            },
                            "health_bonus": {
                                "type": "string",
                                "description": "the health bonus that the created item gives between 0 and 20 ",
                            },
                            "enegy_bonus": {
                                "type": "string",
                                "description": "the energy bonus that the created item gives between 0 and 20 ",
                            },
                            "magic_bonus": {
                                "type": "string",
                                "description": "the magic value of the created item between 0 and 10 ",
                            },
                            "strength_bonus": {
                                "type": "string",
                                "description": "the strength value of the created characted between 0 and 10 ",
                            },
                            "speed_bonus": {
                                "type": "string",
                                "description": "the speed value of the created characted between 0 and 0.5 ",
                            },
                        },
                        "required": ["name","description", "item_type", "health_bonus","enegy_bonus","magic_bonus", "strength_bonus", "speed_bonus"],
                    },
                }
            ],
            function_call={"name":"create_character_json"},
        )
        
    
        message = result["choices"][0]["message"]
        print(message)
        response_option=message.to_dict()['function_call']['arguments']   
        print(response_option)
        options=json.loads(response_option)
        return options

    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return
def read_log_file(file_path):
    with open(file_path, 'r') as log_file:
        log_content = log_file.read()
    return log_content
def function_call_Grant_Portal_Acces(file_path,objective): 
    try:
        logs=read_log_file(file_path)
        print('LOGS : ', logs)
        print('objective : ', objective)
        system_intel = "You are an assistant designed to help me decide if an objective has been fullfiled."
        prompt =f"Given the following player logs: {logs}. Is this objective completed ? objective : {objective} /n give acces to the next floor ? Don't be too severe in the decision. When you are called the player has reached the exit portal, so don't bother with logs about exit portal 444."
        result = openai.ChatCompletion.create(model="gpt-4-0613",
                                    messages=[{"role": "system", "content": system_intel},
                                            {"role": "user", "content": prompt}],
                                            functions=[
                {
                    "name": "Grant_acces",
                    "description": "A function to call to grante acces to the next floor to the player or not.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "acces": {
                                "type": "string",
                                "description": "Does the portal open? 'Yes' or 'No'",
                            },
                        },
                        "required": ["acces"],
                    },
                }
            ],
            function_call={"name":"Grant_acces"},
        )
        
    
        message = result["choices"][0]["message"]
        print(message)
        response_option=message.to_dict()['function_call']['arguments']   
        print(response_option)
        options=json.loads(response_option)
        return options

    except openai.error.OpenAIError as e:
        print("Some error happened here.",e)
        return