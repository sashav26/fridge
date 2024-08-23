from dotenv import load_dotenv
import openai
import os
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

model = SentenceTransformer('all-MiniLM-L6-v2')

def vectorize_text(text):
    return model.encode([text])[0]

def create_faiss_index(embedding_dim, embeddings):
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings.astype('float32'))
    return index

def openai_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that helps with categorizing ingredients and adjusting quantities."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

def classify_or_create_type(ingredient_name, existing_types, index, threshold=0.8):
    ingredient_vector = vectorize_text(ingredient_name).astype('float32')
    D, I = index.search(np.array([ingredient_vector]), 1)
    if D[0][0] < threshold:
        return existing_types[I[0][0]]
    else:
        prompt = f"Create a new type for the ingredient: {ingredient_name}."
        new_type = openai_chat_completion(prompt)
        existing_types.append(new_type)
        new_type_embedding = vectorize_text(new_type).astype('float32')
        index.add(np.array([new_type_embedding]))
        return new_type

def adjust_quantity_units(item_name, item_quantity):
    prompt = f"The item is described as: {item_name}. The detected quantity is: {item_quantity}. Provide the correct quantity and units."
    quantity_units = openai_chat_completion(prompt)
    match = re.match(r'(\d+\.?\d*)\s*([a-zA-Z]+)', quantity_units)
    if match:
        return float(match.group(1)), match.group(2)
    return float(item_quantity), "each"

def process_donut_output(donut_output, existing_types, index):
    processed_data = []
    for item in donut_output.get("line_items", []):
        item_name = item.get("item_name", "Unknown Item")
        detected_quantity = item.get("item_quantity", "1")
        classified_type = classify_or_create_type(item_name, existing_types, index)
        quantity, units = adjust_quantity_units(item_name, detected_quantity)
        item["item_quantity"] = quantity
        item["item_units"] = units
        item["classified_type"] = classified_type
        processed_data.append(item)
    return processed_data
