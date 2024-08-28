from dotenv import load_dotenv
import openai
import os
import re
import numpy as np

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_embedding(text):
    response = openai.Embedding.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return np.array(response['data'][0]['embedding'])

def classify_or_create_type(ingredient_name, existing_types, existing_embeddings, threshold=0.8):
    ingredient_embedding = generate_embedding(ingredient_name)
    similarities = np.dot(existing_embeddings, ingredient_embedding.T)
    
    if np.max(similarities) >= threshold:
        best_match_index = np.argmax(similarities)
        return existing_types[best_match_index]
    else:
        prompt = f"Create a new type for the ingredient: {ingredient_name}."
        new_type = openai_chat_completion(prompt)
        existing_types.append(new_type)
        new_type_embedding = generate_embedding(new_type)
        existing_embeddings = np.vstack([existing_embeddings, new_type_embedding])
        return new_type

def openai_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that helps with categorizing ingredients and adjusting quantities."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

def adjust_quantity_units(item_name, item_quantity):
    prompt = f"The item is described as: {item_name}. The detected quantity is: {item_quantity}. Provide the correct quantity and units."
    quantity_units = openai_chat_completion(prompt)
    match = re.match(r'(\d+\.?\d*)\s*([a-zA-Z]+)', quantity_units)
    if match:
        return float(match.group(1)), match.group(2)
    return float(item_quantity), "each"

def process_donut_output(donut_output, existing_types, existing_embeddings):
    processed_data = []
    for item in donut_output.get("line_items", []):
        item_name = item.get("item_name", "Unknown Item")
        detected_quantity = item.get("item_quantity", "1")
        classified_type = classify_or_create_type(item_name, existing_types, existing_embeddings)
        quantity, units = adjust_quantity_units(item_name, detected_quantity)
        item["item_quantity"] = quantity
        item["item_units"] = units
        item["classified_type"] = classified_type
        processed_data.append(item)
    return processed_data
