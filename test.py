import multiprocessing
import time

# Function to run in the process
def worker_function():
    print("Worker started")
    time.sleep(2)  # Simulating some work
    print("Worker finished")

if __name__ == "__main__":
    # Create a Process object
    process = multiprocessing.Process(target=worker_function)

    # Start the process
    process.start()

    # Wait for the process to finish
    process.join()

    print("Main process finished")