# Install the openai library if not already installed
# !pip install openai

import json
import openai
import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import datetime

from multiprocessing import Pool


# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the questions with choices
questions = [
    {
        "question": "What do you believe is the ideal role of government in society?",
        "choices": {
            "A": "Minimal intervention; government should be as small as possible.",
            "B": "Active role in welfare and regulation to ensure social justice.",
            "C": "Preserve traditional values and maintain national security."
        },
        "category": "Political Ideology",
        "attribute": "government_role"
    },
    {
        "question": "Do you believe a free-market economy or a regulated economy is better for society?",
        "choices": {
            "A": "Free-market economy; minimal regulations.",
            "B": "Regulated economy to prevent inequalities.",
            "C": "A mixed approach balancing freedom and regulation."
        },
        "category": "Economic Beliefs",
        "attribute": "economic_preference"
    },
    {
        "question": "Should individual rights ever be limited for the sake of the collective good?",
        "choices": {
            "A": "Individual rights are paramount and should not be limited.",
            "B": "Yes, if it benefits society as a whole.",
            "C": "Only in extreme cases."
        },
        "category": "Social Values",
        "attribute": "individual_vs_collective"
    },
    {
        "question": "Do you believe in a higher power or deity?",
        "choices": {
            "A": "Yes, and it significantly influences my life.",
            "B": "No, I do not believe in a higher power.",
            "C": "I'm unsure or agnostic."
        },
        "category": "Religious Beliefs",
        "attribute": "belief_in_higher_power"
    },
    {
        "question": "What responsibilities do individuals have toward others in their community or society?",
        "choices": {
            "A": "Strong responsibilities; we should actively help others.",
            "B": "Minimal responsibilities; individuals should focus on themselves.",
            "C": "Some responsibilities, but personal goals come first."
        },
        "category": "Ethical Responsibilities",
        "attribute": "responsibility_to_others"
    }
]


def ask_questions():
    use_existing = input("Do you want to use the existing character map? (Y): ").strip().lower()
    if use_existing == "y" and os.path.exists("character_map.json"):
        with open("character_map.json", "r") as f:
            character_map = json.load(f)
        print("Character map loaded from 'character_map.json'.")
    else:
        print("Please answer the following questions:")
        character_map = []
        h = False
        with open('choices.json', 'r') as f:
            questions = json.load(f)
            for count, choice in enumerate(questions["choices"]):
                print(f"{count + 1}. {choice}")
            while True:
                answer = int(input("Your ideology (1/2/3/4):\nHit 0 for help.").strip())
                if answer == 0:
                    for count, choice in enumerate(questions["choices"]):
                        print(f"{count + 1}. {choice} - {questions[choice]['description']}")
                elif answer > 0 and answer <= len(questions["choices"]):
                    character_map.append(questions[questions["choices"][answer - 1]])
                    break
                else:
                    print("Invalid choice. Please select 1, 2, 3 or 4. Hit 0 for help.")
        save_character_map(character_map)
    return character_map


def save_character_map(character_map):
    with open('character_map.json', 'w') as f:
        json.dump(character_map, f, indent=4)
    print("\nCharacter map saved to 'character_map.json'.")


def pick_philosophers(character_map):
    prompt = f"""
        Based on the following character beliefs:

        {json.dumps(character_map, indent=4)}

        Identify 10 philosophers or authors whose philosophies contrast with these beliefs. Provide a brief description of each philosopher's views, including a summary of their contrasting perspectives.
        Philosophers should be relevant to a general audience.
        """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in philosophy and psychology"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1200,
        n=1,
        stop=None,
        temperature=0.7,
    ) 
    philosophers = response.choices[0].message.content
    return philosophers


def generate_plot(character_map, philosophers):
    prompt = f"""
    Given the character's belief system:

    {json.dumps(character_map, indent=4)}

    Use the philosophical ideas from the following philosophers to inspire the plots:

    {philosophers}

    Create a detailed what if plot contrasting to the character's belief system with anthropomorphic animals as the main characters.
    Plots should be inspired by above philosophers from history and literature.
    Plots should be creative, realistic and relatable to a general audience, but not obvious.
    Plots should be concise, humorous and engaging.
    Philosophers can be part of the plot.
    Create a deeply engaging and thought provoking script with philosophers and character map mentioned above.
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a storyboard writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.7,
    )
    plots = response.choices[0].message.content
    return plots


def generate_storyboard(philosophers, plots, character_map):
    prompt = f"""
            Philosophers:
            {philosophers}

            Plots:
            {plots}

            Evaluate each of the above philosophers and plots and write a thought provoking, understandable for a general audience, relevant 1-liner funny story with relatable and contrasting philosophical insights.
            It should be a single panel comic with a caption and a title.
            It must be easier to describe the settings in a picture than to describe it in words. Do not use text cues in the description.
            Generate a vivid description of the story setting.
            Be inspired by Camus, Dostoevsky, Borges, Kafka, Gary Larson's 'The Far Side' and Bill Watterson's 'Calvin and Hobbes'.
            Make anthropomorphic animals as the main characters.
            JSON output with the following schema:
                "list_of_philosophers": "List of philosophers (names only) that inspired the story",
                "comic_caption": "Punchline for the comic image",
                "comic_description": "Simple description of the setting for a comic image in a way that is easy to generate an image with DALL-E relevant to the comic_caption; no text cues in the description",
                "story": "A deeply meaningful, relevant 1-liner funny story without losing the philosophical insights.",
                "comic_title": "Title of the comic image"
            """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a sharp, witty and relatable philosophical punchline writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        n=1,
        stop=None,
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    story = response.choices[0].message.content
    print("\nFinal Story:\n")
    print(story)
    story = json.loads(story)

    image_url = generate_image_from_description(story["comic_description"], story["comic_caption"])
    story["image_url"] = image_url
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"story_{timestamp}.json"
    with open(filename, "w") as file:
        json.dump(story, file, indent=4)
    return story


def generate_image_from_description(description, caption):
    prompt = f"""
    Create a high quality image in clean pointillism style with no text in the image.
    Image should feel like a comic panel.
    Image should be based on the following description:
    Replace any text with placeholder elements.
    Make anthropomorphic animals as the main characters.

    Make the image relevant to the caption under the image: {caption}
    It should capture the essence of the description and be suitable for a single panel comic.
    Here is the description of the image:
    {description}
    """
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        quality="hd",
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    return image_url


def generate_comic_with_caption(image_url, comic_caption):
    # Download the image
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    # Create a new image with space for the caption
    width, height = image.size
    new_height = height + 100  # Adding space for the caption
    new_image = Image.new("RGB", (width, new_height), "white")
    new_image.paste(image, (0, 0))

    # Add the caption
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.truetype("Comic Sans MS.ttf", 24)
    _, _, text_width, text_height = draw.textbbox((0, 0), "@liminal_comics", font=font)
    text_x = width - (text_width + 20)
    text_y = 15
    draw.text((text_x, text_y), "@liminal_comics", fill="black", stroke_width=2, stroke_fill="white", font=font)
    if len(comic_caption) > 80:
        # If the caption has multiple lines, adjust the text position for each line
        phrases = []
        current_phrase = ""
        for word in comic_caption.split():
            if len(current_phrase) + len(word) + 1 <= 80:
                current_phrase += (word + " ")
            else:
                phrases.append(current_phrase.strip())
                current_phrase = word + " "
        phrases.append(current_phrase.strip())
        for i, line in enumerate(phrases):
            _, _, text_width, text_height = draw.textbbox((0, 0), line, font=font)
            text_x = (width - text_width) // 2
            text_y = height - (40 - text_height) // 2 + i * (text_height + 5)
            draw.text((text_x, text_y), line, fill="black", font=font)
    else:
        # If the caption is a single line, draw it as usual
        _, _, text_width, text_height = draw.textbbox((0, 0), comic_caption, font=font)
        text_x = (width - text_width) // 2
        text_y = height - (20 - text_height) // 2
        draw.text((text_x, text_y), comic_caption, fill="black", font=font)
    # Save the new image
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"comic_{timestamp}.png"
    new_image.save(new_filename)

    return new_filename


def process_story(args):
    philosophers, character_map = args
    plots = generate_plot(character_map, philosophers)
    story = generate_storyboard(philosophers, plots, character_map)
    final_comic = generate_comic_with_caption(story["image_url"], story["comic_caption"])
    return story, final_comic


def main():
    number_of_stories = int(input("How many stories do you want to generate? "))
    character_map = ask_questions()
    philosophers = pick_philosophers(character_map)
    with Pool(number_of_stories) as p:
        p.map(process_story, [(philosophers, character_map) for _ in range(number_of_stories)])


if __name__ == "__main__":
    main()
