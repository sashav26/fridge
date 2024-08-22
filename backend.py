
from config import image_dir, device, processed_dir
from database import setup_database, save_to_database, query_database
from image_inference import generate_text_from_image
from pathlib import Path
import shutil

def main():
    conn, cursor = setup_database()

    processed_dir.mkdir(parents=True, exist_ok=True)


    image_files = [image_file for image_file in image_dir.iterdir() if image_file.suffix == '.png']

    for image_file in image_files:
        extracted_data = generate_text_from_image(str(image_file), device)
        save_to_database(extracted_data, cursor, conn)

        destination = processed_dir / image_file.name
        shutil.move(str(image_file), str(destination))
        print(f"Moved {image_file.name} to {processed_dir}")
        

    query_database(cursor)

    conn.close()

if __name__ == "__main__":
    main()
