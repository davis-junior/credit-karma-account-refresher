import threading


def get_input_with_timeout(prompt, timeout):
    prompt = f"Waiting {timeout} seconds for input...\n{prompt}"

    user_input = []

    def ask_user():
        user_input.append(input(prompt))

    # Start a thread to get input
    input_thread = threading.Thread(target=ask_user)
    input_thread.daemon = True
    input_thread.start()

    # Wait for the thread to complete or timeout
    input_thread.join(timeout)

    if input_thread.is_alive():
        print("\nTimeout! No response received.")
        return None
    else:
        return user_input[0] if user_input else None
