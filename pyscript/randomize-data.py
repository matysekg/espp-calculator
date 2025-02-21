from pyscript import document, window
#import asyncio
import json
from pyodide.ffi.wrappers import add_event_listener



def read_file_content(content):
    try:
        data_dict = json.loads(content)
        # Print the dictionary to the console
        print(data_dict)
        # Display the dictionary on the webpage
        document.getElementById("output").innerText = str(data_dict)
    except json.JSONDecodeError:
        document.getElementById("output").innerText = "Invalid JSON file."

async def upload_file_and_process(e):

    # Get the target of the event
    target = e.target
    jsonFile = document.querySelector('#jsonFile')
    '''    # Iterate over the properties of the target
    attributes = dir(jsonFile)  # Using dir() to get a list of attributes
    for attr in attributes:
        try:
            # Attempt to print the attribute and its value
            print(f"{attr}: {getattr(target, attr)}")
        except Exception as ex:
            # Handle any exceptions (e.g., accessing certain properties might throw errors)
            print(f"Could not access {attr}: {ex}")'''

    file_list = jsonFile.files
    if file_list.length > 0:
        # Get the first file
        first_file = file_list.item(0)
        # Print the name of the file
        print("File name:", first_file.name)
        text = await first_file.text()
        #print(f"File text: {text}" )
        dictionary = json.loads(text)
        #print(f"json: {dictionary}")
    else:
        print("No file selected.")
    


# Add an event listener to the show active sessions checkbox
upload_button = document.querySelector('#uploadButton')
add_event_listener(upload_button,'click', upload_file_and_process)