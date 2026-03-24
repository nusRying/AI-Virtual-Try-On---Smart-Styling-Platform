import requests
import argparse
import os
import time

def test_vto_async(user_image, garment_image, host="http://localhost:8000"):
    """
    End-to-end test for the asynchronous VTO pipeline.
    1. Submits images to the API.
    2. Polls the task status until completion.
    3. Downloads the final image on success.
    """
    url_submit = f"{host}/api/v1/try-on"
    
    if not os.path.exists(user_image):
        print(f"Error: User image not found at {user_image}")
        return
        
    if not os.path.exists(garment_image):
        print(f"Error: Garment image not found at {garment_image}")
        return

    # 1. Submit the task
    print(f"Submitting try-on request for {user_image} and {garment_image}...")
    files = {
        'user_image': open(user_image, 'rb'),
        'garment_image': open(garment_image, 'rb')
    }
    
    response = requests.post(url_submit, files=files)
    
    if response.status_code != 200:
        print(f"Submission failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return

    data = response.json()
    task_id = data.get("task_id")
    print(f"Task submitted! ID: {task_id}")

    # 2. Poll for status
    url_status = f"{host}/api/v1/tasks/{task_id}"
    print("Polling for task completion...")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        status_resp = requests.get(url_status)
        if status_resp.status_code != 200:
            print(f"Status check failed: {status_resp.text}")
            break
            
        status_data = status_resp.json()
        current_status = status_data.get("status")
        print(f"Current Status: {current_status}")
        
        if current_status == 'SUCCESS':
            result_data = status_data.get("result")
            output_path_on_server = result_data.get("output_path")
            filename = os.path.basename(output_path_on_server)
            
            # 3. Download the result
            url_download = f"{host}/api/v1/results/{filename}"
            print(f"Task successful! Downloading from {url_download}...")
            
            dl_resp = requests.get(url_download)
            if dl_resp.status_code == 200:
                local_output = "temp/async_e2e_output.png"
                os.makedirs("temp", exist_ok=True)
                with open(local_output, "wb") as f:
                    f.write(dl_resp.content)
                print(f"Success! Final result saved to {local_output}")
            else:
                print(f"Download failed: {dl_resp.text}")
            break
            
        elif current_status == 'FAILURE':
            print(f"Task failed: {status_data.get('error')}")
            break
            
        retry_count += 1
        time.sleep(2)
        
    if retry_count == max_retries:
        print("Polling timed out.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, help="Path to user image")
    parser.add_argument("--garment", type=str, help="Path to garment image")
    parser.add_argument("--host", type=str, default="http://localhost:8000")
    args = parser.parse_args()
    
    # Ensure images exist or provide defaults for documentation
    user_img = args.user or "tests/samples/user.jpg"
    garment_img = args.garment or "tests/samples/shirt.jpg"
    
    test_vto_async(user_img, garment_img, args.host)
