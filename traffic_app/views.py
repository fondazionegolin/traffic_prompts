from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
import os
import random
import string
from datetime import datetime

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
    prompts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prompts', 'visual_prompts.json')
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
        try:
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
            
            with open(user_data_path, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
            # Save prompts separately with just the code
            prompts_filename = f"{data['codice']}.json"
            prompts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prompts', prompts_filename)
            
            with open(prompts_path, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)
            
            return JsonResponse({"status": "success", "message": "Data saved successfully"})
            
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
