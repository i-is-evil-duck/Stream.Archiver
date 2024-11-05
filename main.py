# main.py
import threading
import upload
# import record
import console
import clear

def start_clear_task():
    """Starts the clear.py scheduler in a separate thread."""
    clear.start_clear_scheduler()

def main():
    # Create and start each service thread
    upload_thread = threading.Thread(target=upload.start_upload_monitor)
    # record_thread = threading.Thread(target=record.start_recording)
    console_thread = threading.Thread(target=console.start_console)
    clear_thread = threading.Thread(target=start_clear_task)  # Thread for clear scheduler

    # Set clear_thread as a daemon so it doesn't block program exit
    clear_thread.daemon = True

    # Start all threads
    upload_thread.start()
    # record_thread.start()
    console_thread.start()
    clear_thread.start()

    print("All services started successfully.")

    # Join threads to wait for completion
    upload_thread.join()
    # record_thread.join()
    console_thread.join()
    # Note: clear_thread does not need join as it runs continuously in the background

if __name__ == "__main__":
    main()
