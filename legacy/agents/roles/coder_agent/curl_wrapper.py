import subprocess

def run_curl_command(command_args, output_file=None):
    """
    Runs a curl command and handles its output.

    Args:
        command_args (list): A list of strings representing the curl command and its arguments.
        output_file (str, optional): Path to a file where curl's output should be saved.
                                     If None, output is captured and returned.

    Returns:
        dict: A dictionary containing 'status' ('success' or 'error'), 'message', and 'output' (if output_file is None).
    """
    full_command = ["curl", "-s"] + command_args

    try:
        if output_file:
            with open(output_file, 'w') as f:
                process = subprocess.run(full_command, stdout=f, stderr=subprocess.PIPE, check=True, text=True)
            return {
                "status": "success",
                "message": f"Content successfully saved to {output_file}",
                "output": ""
            }
        else:
            process = subprocess.run(full_command, capture_output=True, check=True, text=True)
            return {
                "status": "success",
                "message": "Curl command executed successfully.",
                "output": process.stdout
            }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Curl command failed with error: {e.stderr}",
            "output": e.stderr
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Curl command not found. Please ensure curl is installed and in your PATH.",
            "output": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "output": ""
        }

if __name__ == "__main__":
    # Example Usage:
    # 1. Basic GET request, output to console
    print("--- Example 1: Basic GET request (output to console) ---")
    result = run_curl_command(["https://www.example.com"])
    print(result)

    # 2. Basic GET request, save to file
    print("\n--- Example 2: Basic GET request (save to file) ---")
    test_output_file = "example_output.html"
    result = run_curl_command(["https://www.example.com"], output_file=test_output_file)
    print(result)
    if result["status"] == "success":
        print(f"Check {test_output_file} for content.")

    # 3. Simulate an error (e.g., invalid URL)
    print("\n--- Example 3: Simulate an error (invalid URL) ---")
    result = run_curl_command(["https://invalid.url.nonexistent"])
    print(result)

    # 4. Simulate a POST request with data (output to console)
    print("\n--- Example 4: Simulate a POST request with data ---")
    result = run_curl_command(["-X", "POST", "-d", "param1=value1&param2=value2", "https://httpbin.org/post"])
    print(result)
