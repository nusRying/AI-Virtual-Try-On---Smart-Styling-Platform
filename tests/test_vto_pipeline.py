import requests
import argparse
import os

def test_try_on(user_image, garment_image, host="http://localhost:8000"):
    url = f"{host}/api/v1/try-on"
    
    if not os.path.exists(user_image):
        print(f"Error: User image not found at {user_image}")
        return
        
    if not os.path.exists(garment_image):
        print(f"Error: Garment image not found at {garment_image}")
        return

    print(f"Sending try-on request for {user_image} and {garment_image}...")
    
    files = {
        'user_image': open(user_image, 'rb'),
        'garment_image': open(garment_image, 'rb')
    }
    
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        output_path = "temp/e2e_output.png"
        os.makedirs("temp", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Success! Merged result saved to {output_path}")
    else:
        print(f"Request failed with status {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, help="Path to user image")
    parser.add_argument("--garment", type=str, help="Path to garment image")
    parser.add_argument("--host", type=str, default="http://localhost:8000")
    args = parser.parse_args()
    
    # Example usage:
    # python tests/test_vto_pipeline.py --user tests/samples/user.jpg --garment tests/samples/shirt.jpg
    
    test_try_on(args.user, args.garment, args.host)
