from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
import os
import random
import string
from datetime import datetime
from django.conf import settings

from pythonosc import udp_client

# Create your views here.

def generate_code():
    # Generate a 4-character random code using letters and numbers
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=4))

def get_random_words():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'word_dictionary.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        word_dict = json.load(file)
    
    random_words = {
        'infanzia': random.sample(word_dict['infanzia'], 9),
        'maturita': random.sample(word_dict['maturita'], 9),
        'vecchiaia': random.sample(word_dict['vecchiaia'], 9)
    }
    return random_words

def get_prompts_for_words(selected_words):
    # Load prompts
    prompts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prompts', 'visual_prompts_new.json')
    with open(prompts_path, 'r', encoding='utf-8') as file:
        all_prompts = json.load(file)
    
    # Initialize the result dictionary
    result = {
        "infanzia": [],
        "maturita": [],
        "vecchiaia": []
    }
    
    # For each life phase
    for phase in ["infanzia", "maturita", "vecchiaia"]:
        # Get the selected words for this phase
        phase_words = selected_words.get(phase, [])
        
        # Find matching prompts from visual_prompts.json
        available_prompts = all_prompts.get(phase, [])
        
        # For each selected word, find its corresponding prompt
        for word in phase_words:
            matching_prompt = next(
                (prompt for prompt in available_prompts if prompt["word"] == word),
                None
            )
            if matching_prompt:
                result[phase].append(matching_prompt)
            else:
                # If no prompt found, create a default one
                result[phase].append({
                    "word": word,
                    "prompt": f"Create a scene that captures the essence of {word}",
                    "live_clip": "default"
                })
    
    return result

@ensure_csrf_cookie
def index(request):
    words = get_random_words()
    user_code = generate_code()
    return render(request, 'traffic_app/index.html', {
        'words': words,
        'user_code': user_code
    })

@csrf_exempt
def save_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract selected words
        selected_words = {
            "infanzia": data.get("infanzia", []),
            "maturita": data.get("maturita", []),
            "vecchiaia": data.get("vecchiaia", [])
        }

        # Get corresponding prompts
        prompts = get_prompts_for_words(selected_words)

        # Create the combined data structure
        combined_data = {
            "user_data": {
                "codice": data.get("codice", ""),
                "sesso": data.get("sesso", ""),
                "eta": data.get("eta", ""),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            "selections": selected_words,
            "prompts": prompts
        }

        # Save user data with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_data_filename = f"{timestamp}_{data['codice']}.json"
        user_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_selections', user_data_filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(user_data_path), exist_ok=True)

        with open(user_data_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)

        # Save prompts separately with just the code
        prompts_filename = f"{data['codice']}.json"
        prompts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prompts', prompts_filename)

        # Ensure the prompts directory exists
        os.makedirs(os.path.dirname(prompts_path), exist_ok=True)

        # Save both user data and prompts in the prompts file
        prompts_data = {
            "user_data": {
                "codice": data.get("codice", ""),
                "sesso": data.get("sesso", ""),
                "eta": data.get("eta", "")
            },
            "infanzia": prompts["infanzia"],
            "maturita": prompts["maturita"],
            "vecchiaia": prompts["vecchiaia"]
        }

        with open(prompts_path, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)

        client = udp_client.SimpleUDPClient(settings.TOUCH_HOST, 8008)
        client.send_message("/visitor", [data['codice']])

        return JsonResponse({"status": "success", "message": "Data saved successfully"})
            

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@csrf_exempt
def get_prompts(request):
    try:

        visitor = request.GET.get('visitor', "")

        if visitor:
            json_path = os.path.join(settings.JSON_FOLDER, "{}.json".format(visitor))

            with open(json_path, 'r') as f:
                prompts = json.load(f, )
            
            return JsonResponse(prompts, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in prompts file'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def wait(request, user_code):
    return render(request, 'traffic_app/wait.html', {
        'user_code': user_code
    })