# main.py
import threading
import upload
import record
import console

def main():
    # Start each script in its own thread
    upload_thread = threading.Thread(target=upload.start_upload_monitor)
    record_thread = threading.Thread(target=record.start_recording)
    console_thread = threading.Thread(target=console.start_console)

    # Start all threads
    upload_thread.start()
    record_thread.start()
    console_thread.start()

    print("All services started successfully.")

    # Join threads to wait for completion
    upload_thread.join()
    record_thread.join()
    console_thread.join()

if __name__ == "__main__":
    main()
