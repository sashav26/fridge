import torch
import re
from dotenv import load_dotenv
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel


processor = DonutProcessor.from_pretrained("AdamCodd/donut-receipts-extract")
model = VisionEncoderDecoderModel.from_pretrained("AdamCodd/donut-receipts-extract")
model.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

def load_and_preprocess_image(image_path: str):
    
    image = Image.open(image_path).convert("RGB") 
    pixel_values = processor(image, return_tensors="pt").pixel_values
    return pixel_values

def generate_text_from_image(image_path: str, device):
    """
    Generate text from an image using the trained model.
    """
    pixel_values = load_and_preprocess_image(image_path)
    pixel_values = pixel_values.to(device)
    
    model.eval()
    with torch.no_grad():
        task_prompt = "<s_receipt>"
        decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids
        decoder_input_ids = decoder_input_ids.to(device)
        generated_outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=model.decoder.config.max_position_embeddings, 
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            early_stopping=True,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True
        )

    decoded_text = processor.batch_decode(generated_outputs.sequences)[0]
    decoded_text = decoded_text.replace(processor.tokenizer.eos_token,"").replace(processor.tokenizer.pad_token,"")
    decoded_text = re.sub(r"<.*?>", "", decoded_text, count = 1).strip()
    decoded_text = processor.token2json(decoded_text)
    print ("extracted data:", decoded_text)
    return decoded_text
       
