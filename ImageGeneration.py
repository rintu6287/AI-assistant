import os
import requests
from PIL import Image
from time import sleep
from dotenv import dotenv_values

# Load .env
env_vars = dotenv_values(".env")
HF_API_KEY = env_vars.get("HuggingFaceAPIKey")

# HuggingFace model
HF_MODEL = "stabilityai/stable-diffusion-2-1"

# Get project directories
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_folder = os.path.join(project_root, "Data")
os.makedirs(data_folder, exist_ok=True)

def generate_image_hf(prompt: str, out_path: str):
    """Generate image using HuggingFace Inference API"""
    print(f"Generating image for prompt: {prompt}")
    
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}  # wait if model is loading
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e} - {response.text}")
        return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False

    try:
        # HuggingFace returns image bytes
        img_data = response.content
        with open(out_path, "wb") as f:
            f.write(img_data)
        print(f"Image saved to {out_path}")
        return True
    except Exception as e:
        print(f"Failed to save image: {e}")
        return False

def open_image(path: str):
    """Open the saved image"""
    try:
        img = Image.open(path)
        img.show()
        sleep(1)
    except Exception as e:
        print(f"Unable to open {path}: {e}")

def generate_and_open(prompt: str):
    prompt_safe = prompt.replace(" ", "_")
    out_path = os.path.join(data_folder, f"{prompt_safe}.png")
    
    if generate_image_hf(prompt, out_path):
        open_image(out_path)

if __name__ == "__main__":
    while True:
        prompt = input("Enter image prompt (or 'exit' to quit): ")
        if prompt.lower() in ["exit", "quit"]:
            break
        generate_and_open(prompt)
