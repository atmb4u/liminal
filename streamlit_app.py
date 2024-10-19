import streamlit as st
import json
import os
from liminal import pick_philosophers, process_story


# Set up the Streamlit app
st.title("Liminal Comics")
st.write(
    "This app generates philosophical comics that contrasts your ideology with the philosophy of a famous philosophers."
    "You can select your ideology from the dropdown menu."
    "Please provide your OpenAI API key to try it out. https://platform.openai.com/api-keys"
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = openai_api_key

# Load or create character map
use_existing = st.checkbox("Use existing character map if available", value=False)
character_map = []
if use_existing and os.path.exists("character_map.json"):
    with open("character_map.json", "r") as f:
        character_map = json.load(f)
        st.success("Character map loaded from 'character_map.json'.")
else:
    with open('choices.json', 'r') as f:
        ideology = json.load(f) 
    answer = st.multiselect("Please select your political ideology:", list(ideology["choices"]))
    for a in answer:
        character_map.append(ideology[a])
        st.success("%s: %s" % (a, ideology[a]["description"]))

    # Save the character map
    with open('character_map.json', 'w') as f:
        json.dump(character_map, f, indent=4)

    # Generate philosophers and story
    if st.button("Convince me otherwise"):
        philosophers = pick_philosophers(character_map)
        story, final_comic = process_story((philosophers, character_map))
        st.header("Food for Thought")
        st.subheader(story["comic_title"])
        st.image(final_comic)
        st.write(story["story"])
        st.write("Philosophers: " + ", ".join(story["list_of_philosophers"]))
        st.write(story["comic_description"])
