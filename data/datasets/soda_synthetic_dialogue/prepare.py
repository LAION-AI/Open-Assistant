"""Prepare the SODA Synthetic Dialogue Dataset"""

import json
import os
import random
import sys

from datasets import load_dataset
from tqdm import tqdm

# adapted from https://colab.research.google.com/drive/1Sw3px5dP8whdqT7QMNoqwmqIasZkMbJi?usp=sharing

SUMMARY_TEMPLATE = """User: Can you give me a short story description for this dialogue?
  {dialogue}
Assistant: Sure, a short story description for this dialogue could be:
  {story}
User: And a title?
Assistant: Sure, a title for this dialogue could be:
  {title}"""

THEME_TEMPLATE = """
User: What would be one theme of this story?
Assistant: One theme of this story could be:
  {theme}"""

NEW_DIALOGUE_TEMPLATE = """User: Can you write a short dialogue based on this story:
  {story}
Assistant: Sure, a dialogue for this story could be:
  {dialogue}
User: And a title?
Assistant: Sure, a title for this dialogue could be:
  {title}"""

NEXT_LINES_TEMPLATE = """User: Can you write the next few lines of dialogue for this scene:
  {scene}
Assistant: Sure, the next dialogue for this scene could be:
  {dialogue}
User: And a title?
Assistant: Sure, a title for this dialogue could be:
  {title}
User: How about a short description?
Assistant: Sure, a short description for this dialogue could be:
  {story}"""

NEW_STORY_AND_DIALOGUE_TEMPLATE = """User: Can you write a short story and dialogue about:
  {title1}
Assistant: Sure, a short story and dialogue about: "{title1}" could be:
  {story}"""

FULL_DIALOGUE_TEMPLATE = """{conversation}
  {dialogue}"""

MORE_DIALOGUE_TEMPLATE = """{conversation}
  {dialogue1}
User: Can you provide more dialogue assuming "{title2}"?
Assistant: Sure, the next dialogue for this scene could be:
  {dialogue2}"""

NEXT_DIALOGUE_TEMPLATE = """{conversation}
  {dialogue1}
User: More please.
Assistant: Sure, the next dialogue for this scene could be:
  {dialogue2}"""

NEW_STORY_AND_DIALOGUE_FROM_THEME_TEMPLATE = """User: Can you write short story and dialogue based on the theme:
  {theme}
Assistant: Sure, a short story and dialogue based on the theme "{theme}" could be:
  {story}
  {dialogue}
User: And a title?
Assistant: Sure, a title for this dialogue could be:
  {title}"""

PRINT = len(sys.argv) > 1 and sys.argv[1] == "--print"


def main(output_dir: str = "data"):
    """Download and prepare the dataset for use."""

    random.seed(42)
    dataset = load_dataset("allenai/soda")
    os.makedirs(output_dir, exist_ok=True)

    for split in ["train", "test", "validation"]:
        with open(f"{output_dir}/{split}.jsonl", "w", encoding="utf8") as output:
            for i in tqdm(range(len(dataset[split])), desc=split):
                dat = dataset["train"][i]
                title = dat["literal"]
                story = dat["narrative"]

                if dat["relation"] == "xWant":
                    theme = "wanting " + dat["tail"]
                elif dat["relation"] == "xNeed":
                    theme = "needing " + dat["tail"]
                elif not dat["tail"].startswith("to ") and not dat["tail"].startswith("and "):
                    theme = "being " + dat["tail"]
                elif dat["tail"].startswith("and "):
                    theme = "people are " + dat["tail"].replace("and PersonY ", "")
                else:
                    theme = dat["tail"]
                theme = theme.replace("PersonY", "another person")
                theme = theme.replace("being is", "being")

                dialogue = [s2 + ": " + s1 for s1, s2 in zip(dat["dialogue"], dat["speakers"])]

                if random.randint(0, 6) == 0:
                    # print("##")
                    # print(f"User: Can you give me a short story description for this dialog?")
                    # print("  " + "\n  ".join(dialog))
                    # print(f"Assistant: Sure, a short story description for this dialog could be: \n  {story}")
                    # print("User: And a title?")
                    # print(f"Assistant: Sure, a title for this dialog could be: \n  {title}")
                    # if theme:
                    #     print("User: What would be one theme of this story?")
                    #     print(f'Assistant: One theme of this story could be: "{theme}"')
                    conversation = SUMMARY_TEMPLATE.format(dialogue="\n  ".join(dialogue), story=story, title=title)
                    if theme:
                        conversation = conversation + THEME_TEMPLATE.format(theme=theme)
                elif random.randint(0, 6) == 0:
                    # print("##")
                    # print(f"User: Can you write a short dialog based on this story:\n  {story}")
                    # print(f"Assistant: Sure, a dialog for this story could be:")
                    # print("  " + "\n  ".join(dialog))
                    # print("User: And a title?")
                    # print(f"Assistant: Sure, a title for this dialog could be: \n  {title}")
                    # if theme:
                    #     print("User: What would be one theme of this story?")
                    #     print(f'Assistant: One theme of this story could be: "{theme}"')
                    conversation = NEW_DIALOGUE_TEMPLATE.format(
                        story=story, dialogue="\n  ".join(dialogue), title=title
                    )
                    if theme:
                        conversation = conversation + THEME_TEMPLATE.format(theme=theme)
                elif random.randint(0, 3) == 0:
                    # print("##")
                    # print(f"User: Can you write the next few lines of dialog for this scene:")
                    # if random.randint(0, 1) == 0:
                    #     print("  " + "\n  ".join(dialog[:-5]))
                    #     print(f"Assistant: Sure, the next dialog for this scene could be:")
                    #     print("  " + "\n  ".join(dialog[-5:]))
                    # elif random.randint(0, 1) == 0:
                    #     print("  " + "\n  ".join(dialog[:-3]))
                    #     print(f"Assistant: Sure, the next dialog for this scene could be:")
                    #     print("  " + "\n  ".join(dialog[-3:]))
                    # else:
                    #     print("  " + "\n  ".join(dialog[:-4]))
                    #     print(f"Assistant: Sure, the next dialog for this scene could be:")
                    #     print("  " + "\n  ".join(dialog[-4:]))
                    # print("User: And a title?")
                    # print(f"Assistant: Sure, a title for this dialog could be: \n  {title}")
                    # print("User: How about a short description?")
                    # print(f"Assistant: Sure, a short description for this dialog could be: \n  {story}")
                    # if theme:
                    #     print("User: What would be one theme of this story?")
                    #     print(f'Assistant: One theme of this story could be: "{theme}"')
                    if random.randint(0, 1) == 0:
                        depth = -5
                    elif random.randint(0, 1) == 0:
                        depth = -3
                    else:
                        depth = -4
                    conversation = NEXT_LINES_TEMPLATE.format(
                        scene="\n  ".join(dialogue[:depth]),
                        dialogue="\n  ".join(dialogue[depth:]),
                        title=title,
                        story=story,
                    )
                    if theme:
                        conversation = conversation + THEME_TEMPLATE.format(theme=theme)
                elif random.randint(0, 3) == 0:
                    # print("##")
                    # title1 = title.split(".")[0]
                    # title2 = title.split(".")[1]
                    # print(f"User: Can you write short story and dialog about: {title1}")
                    # print(f'Assistant: Sure, a short story and dialog about: "{title1}" could be:')
                    # print(f"  {story}")
                    # if random.randint(0, 1) == 0:
                    #     print("  " + "\n  ".join(dialog))
                    # elif random.randint(0, 1) == 0 and len(dialog) > 5:
                    #     print("  " + "\n  ".join(dialog[:-5]))
                    #     print(f'User: Can you provide more dialog assuming "{title2}"?')
                    #     print(f"Assistant: Sure, the next dialog for this scene could be:")
                    #     print("  " + "\n  ".join(dialog[-5:]))
                    # elif random.randint(0, 1) == 0:
                    #     print("  " + "\n  ".join(dialog[:-3]))
                    #     print("User: more please.")
                    #     print(f"Assistant: Sure, the next dialog for this scene could be:")
                    #     print("  " + "\n  ".join(dialog[-3:]))
                    # else:
                    #     print("  " + "\n  ".join(dialog[:-4]))
                    #     print(f'User: Can you provide more dialog assuming "{title2}"?')
                    #     print(f"Assistant: Sure, the next dialog for this scene could be:")
                    #     print("  " + "\n  ".join(dialog[-4:]))
                    # if theme:
                    #     print("User: What would be one theme of this story?")
                    #     print(f'Assistant: One theme of this story could be: "{theme}"')
                    title1 = title.split(".")[0]
                    title2 = title.split(".")[1]
                    conversation = NEW_STORY_AND_DIALOGUE_TEMPLATE.format(title1=title1, story=story)
                    if random.randint(0, 1) == 0:
                        conversation = FULL_DIALOGUE_TEMPLATE.format(
                            conversation=conversation, dialogue="\n  ".join(dialogue)
                        )
                    elif random.randint(0, 1) == 0 and len(dialogue) > 5:
                        conversation = MORE_DIALOGUE_TEMPLATE.format(
                            conversation=conversation,
                            dialogue1="\n  ".join(dialogue[:-5]),
                            title2=title2,
                            dialogue2="\n  ".join(dialogue[-5:]),
                        )
                    elif random.randint(0, 1) == 0:
                        conversation = NEXT_DIALOGUE_TEMPLATE.format(
                            conversation=conversation,
                            dialogue1="\n  ".join(dialogue[:-3]),
                            dialogue2="\n  ".join(dialogue[-3:]),
                        )
                    else:
                        conversation = MORE_DIALOGUE_TEMPLATE.format(
                            conversation=conversation,
                            dialogue1="\n  ".join(dialogue[:-4]),
                            title2=title2,
                            dialogue2="\n  ".join(dialogue[-4:]),
                        )
                    if theme:
                        conversation = conversation + THEME_TEMPLATE.format(theme=theme)
                else:
                    # print("##")
                    # print(f"User: Can you write short story and dialog based on the theme:\n  {theme}")
                    # print(f'Assistant: Sure, a short story and dialog based on the theme "{theme}" could be:')
                    # print(f"  {story}")
                    # print("  " + "\n  ".join(dialog))
                    # print("User: And a title?")
                    # print(f"Assistant: Sure, a title for this dialog could be: \n  {title}")
                    conversation = NEW_STORY_AND_DIALOGUE_FROM_THEME_TEMPLATE.format(
                        theme=theme, story=story, dialogue="\n  ".join(dialogue), title=title
                    )
                if PRINT:
                    print("##")
                    print(conversation)

                output.write(f"{json.dumps({'conversation': conversation})}\n")


if __name__ == "__main__":
    sys.exit(main())
