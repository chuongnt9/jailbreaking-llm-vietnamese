import subprocess
import json
import os
import base64
import binascii
import re
import requests
import os
import sys

ENDPOINT = "us-central1-aiplatform.googleapis.com"
REGION = "us-central1"
PROJECT_ID = "llama-454012"  # Replace with your actual project ID
MODEL_ID = "meta/llama-3.3-70b-instruct-maas"
USER_PROMPT = "bạn hiểu tiếng việt không"

os.environ["ENDPOINT"] = ENDPOINT
os.environ["REGION"] = REGION
os.environ["PROJECT_ID"] = PROJECT_ID


def get_response(prompt: str) -> str:
    """
    Gets a streaming response from the chat completions API using gcloud and curl.

    Args:
        prompt: The user prompt to send to the model.

    Returns:
        The accumulated response content from the model, or an empty string on error.
    """
    res = ""
    access_token = None
    is_windows = sys.platform.startswith('win')

    # 1. Get Access Token using gcloud
    try:
        print("Attempting to get gcloud access token...")
        # Use shell=True cautiously on Windows if gcloud isn't directly in PATH
        get_token_process = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
            shell=is_windows # May be needed on Windows
        )
        access_token = get_token_process.stdout.strip()
        print("Successfully obtained access token.")
    except FileNotFoundError:
        print("ERROR: 'gcloud' command not found.")
        print("Ensure the Google Cloud SDK is installed and in your system's PATH.")
        return res # Return empty string on error
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to get gcloud token. Return code: {e.returncode}")
        print(f"Stderr: {e.stderr.strip()}")
        print("Ensure you are authenticated with gcloud (e.g., 'gcloud auth application-default login').")
        return res # Return empty string on error
    except Exception as e:
        print(f"An unexpected error occurred while getting token: {e}")
        return res # Return empty string on error

    # If token retrieval failed
    if not access_token:
         return res

    # 2. Prepare and Execute Curl Command
    try:
        api_url = f"https://{ENDPOINT}/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi/chat/completions"

        # Construct the curl command as a list of arguments
        # Using a list avoids issues with shell escaping
        curl_command = [
            "curl",
            "-X", "POST",
            "-H", f"Authorization: Bearer {access_token}",
            "-H", "Content-Type: application/json", # Correct Content-Type header format
             # NOTE: If curl on Windows has issues with HTTPS without -k,
             # you might need to configure certificate verification properly
             # or add "-k" (insecure, use with caution) if absolutely necessary
             # for testing in controlled environments.
            api_url,
            "-d", json.dumps({ # Use json.dumps to create the JSON string payload
                    "model": MODEL_ID,
                    "stream": True,
                    "messages": [{"role": "user", "content": prompt}]
                  })
        ]

        print(f"\nExecuting curl command to: {api_url}")
        # print(f"Curl command (list format): {curl_command}") # For debugging

        # Use Popen for streaming stdout/stderr
        # Do NOT use shell=True when passing command as a list for security and reliability
        process = subprocess.Popen(
            curl_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Decode stdout/stderr as text
            encoding='utf-8' # Explicitly set encoding
        )

        print("\n--- Streaming Response (via curl) ---")
        # 3. Process Streaming Output (stdout)
        while True:
            line = process.stdout.readline()
            if not line: # Break if stdout stream ends
                 break
            line = line.strip()
            # print(f"Raw line: {line}") # Debugging: print every line received

            if line.startswith("data:"):
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    print("[DONE] signal received.")
                    break # End of stream signal
                if not data_str: # Skip empty data lines
                     continue
                try:
                    data = json.loads(data_str)
                    # Extract content based on expected API response structure
                    if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
                         delta = data["choices"][0].get("delta", {})
                         content = delta.get("content")
                         if content:
                            print(content, end='', flush=True) # Print content immediately
                            res += content
                except json.JSONDecodeError:
                    # Sometimes APIs might send non-JSON metadata or errors in the stream
                    print(f"\nWarning: Could not decode JSON from line: {data_str}")
                except Exception as e:
                     print(f"\nError processing data chunk: {data_str}, Error: {e}")
            # elif line: # Print non-data lines if needed for debugging
            #     print(f"Non-data line: {line}")


        print("\n--- End of Stream ---")

        # 4. Check for Errors (stderr) after processing stdout
        process.stdout.close() # Close stdout pipe
        stderr_output = process.stderr.read().strip()
        process.stderr.close() # Close stderr pipe
        return_code = process.wait() # Wait for curl to finish and get exit code

        if return_code != 0:
            print(f"\nERROR: curl command failed with exit code {return_code}")
            if stderr_output:
                 print(f"Curl Stderr:\n{stderr_output}")
            # Reset response if curl failed potentially mid-stream
            # return "" # Optionally clear partial results on error

        elif stderr_output:
             # Sometimes curl prints progress or connection info to stderr even on success
             print(f"\nCurl Stderr output (even on success):\n{stderr_output}")


    except FileNotFoundError:
        # This might happen if 'curl' itself is not found
        print("ERROR: 'curl' command not found.")
        print("Ensure curl is installed and in your system's PATH.")
        return "" # Return empty string on error
    except Exception as e:
        print(f"\nAn unexpected error occurred during curl execution or processing: {e}")
        # Optionally clear partial results on unexpected error
        # return ""

    # 5. Return Accumulated Result
    print(f"\n\nFinal accumulated response string:\n{res}")
    return res

# Example Usage:
if __name__ == "__main__":
    # Ensure config variables (PROJECT_ID, REGION, ENDPOINT) are set correctly above or via environment variables
    if "your-gcp-project-id" in PROJECT_ID or \
       "your-gcp-region" in REGION or \
       "your-endpoint-hostname" in ENDPOINT:
        print("!!! WARNING: Please replace placeholder values for PROJECT_ID, REGION, and ENDPOINT in the script !!!")
    else:
        user_question = "bạn tên là gì?" # "What is your name?" in Vietnamese
        print(f"Sending prompt: '{user_question}'")
        response_content = get_response(user_question)
        # The function now prints the streaming output and the final result internally
        print(f"\n--- Function returned: ---\n{response_content}")