from config import image_dir, device, processed_dir
from database import setup_database, save_to_database, query_database
from donut_base import generate_text_from_image
from gpt import process_donut_output, vectorize_text, create_faiss_index
from pathlib import Path
import shutil
import numpy as np

def main():
    conn, cursor = setup_database()
    processed_dir.mkdir(parents=True, exist_ok=True)

    existing_types = ["Green Bell Pepper", "Brown Sugar", "Pasta", "Bananas", "Milk", "Lemon", "Strawberries", "Avocados", "Hummus", "Basil"]
    type_embeddings = np.array([vectorize_text(t) for t in existing_types]).astype('float32')
    embedding_dim = type_embeddings.shape[1]
    index = create_faiss_index(embedding_dim, type_embeddings)

    image_files = [image_file for image_file in image_dir.iterdir() if image_file.suffix == '.png']

    for image_file in image_files:
        extracted_data = generate_text_from_image(str(image_file), device)
        processed_data = process_donut_output(extracted_data, existing_types, index)
        save_to_database({"line_items": processed_data}, cursor, conn)
        shutil.move(str(image_file), str(processed_dir / image_file.name))
        print(f"Moved {image_file.name} to {processed_dir}")

    query_database(cursor)
    conn.close()

if __name__ == "__main__":
    main()
