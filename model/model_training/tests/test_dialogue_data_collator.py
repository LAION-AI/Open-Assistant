import pytest
import torch
from model_training.custom_datasets.dialogue_collator import DialogueDataCollator
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS, create_dataset_entry_qa
from model_training.utils.utils import match_tokenizer_name
from transformers.models.auto.tokenization_auto import AutoTokenizer


@pytest.fixture
def pythia_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained("tests/resources/data_collator", local_files_only=True)
    # for this test we use the pythia special tokens but note that this test is model agnostic
    tokenizer_config = match_tokenizer_name("pythia")

    tokenizer.add_special_tokens(
        {
            "pad_token": tokenizer_config.special_tokens.pad_token,
            "eos_token": tokenizer_config.special_tokens.eos_token,
            "sep_token": tokenizer_config.special_tokens.sep_token,
        }
    )

    additional_special_tokens = list(QA_SPECIAL_TOKENS.values())

    tokenizer.add_special_tokens({"additional_special_tokens": additional_special_tokens})
    return tokenizer


def test_dataset_entry_no_context(pythia_tokenizer):
    d = DialogueDataCollator(
        tokenizer=pythia_tokenizer,
        padding=True,
        system_add_length=False,
    )
    features = [
        create_dataset_entry_qa(
            mode="sft",
            questions=["Dummy Question?"],
            answers=["Dummy Answer."],
        )
    ]
    batch = d(features)
    expected_decoded_input_ids = [
        "<|prompter|>Dummy Question?<|endoftext|>" + "<|assistant|>Dummy Answer.<|endoftext|>"
    ]
    expected_decoded_targets = [
        expected_decoded_input_ids[0][len("<|prompter|>") :] + expected_decoded_input_ids[0][: len("<|prompter|>")],
    ]

    expected_masked = ["<|assistant|>Dummy Answer."]

    assert pythia_tokenizer.decode(batch.input_ids[0]) == expected_decoded_input_ids[0]
    # check if targets are as expected
    assert pythia_tokenizer.decode(batch.targets[0]) == expected_decoded_targets[0]

    # check if masking is correct. Note that we mask the system as well
    assert pythia_tokenizer.decode(batch.input_ids[0][batch.label_masks[0]]) == expected_masked[0]


def test_dataset_entry(pythia_tokenizer):
    d = DialogueDataCollator(
        tokenizer=pythia_tokenizer,
        padding=True,
        use_system_tag=True,
        system_property_dropout=0,
        system_add_length=False,
    )
    features = [
        create_dataset_entry_qa(
            mode="sft",
            questions=["What are the risks of untreated type 1 diabetes?"],
            answers=[
                "Untreated type 1 diabetes can rapidly result in diabetic ketoacidosis which may lead to loss of consciousness, coma and death."
            ],
            context="Prolonged lack of insulin can also result in diabetic ketoacidosis, characterized by persistent fatigue, dry or flushed skin, abdominal pain, nausea or vomiting, confusion, trouble breathing, and a fruity breath odor. Blood and urine tests reveal unusually high glucose and ketones in the blood and urine. Untreated ketoacidosis can rapidly progress to loss of consciousness, coma, and death. The percentage of children whose type 1 diabetes begins with an episode of diabetic ketoacidosis varies widely by geography, as low as 15% in parts of Europe and North America, and as high as 80% in the developing world.",
        ),
        create_dataset_entry_qa(
            mode="sft",
            questions=["Find all of the Amsterdam museums mentioned in the text and put them in a numbered list."],
            answers=[
                "The Amsterdam museums mentioned in this text are:\n1. Rijksmuseum\n2. Van Gogh Museum\n3. Amsterdam Museum\n4. Stedelijk Museum\n5. Hermitage Amsterdam\n6. Anne Frank House\n7. Het Scheepvaartmuseum\n8. NEMO"
            ],
            context="Amsterdam's main attractions include its historic canals; the Rijksmuseum, the state museum with a vast collection of Dutch Golden Age art; the Van Gogh Museum; the Dam Square, where the Royal Palace of Amsterdam and former city hall (stadhuis) are located; the Amsterdam Museum; Stedelijk Museum, with modern art; Hermitage Amsterdam, the Concertgebouw concert hall; the Anne Frank House; the Het Scheepvaartmuseum, the Heineken Experience, the Natura Artis Magistra; Hortus Botanicus, NEMO, the red-light district and many cannabis coffee shops. The city is also well known for its nightlife and festival activity; with several of its nightclubs (Melkweg, Paradiso) among the world's most famous. Primarily known for its artistic heritage, elaborate canal system and narrow canal houses with gabled façades; well-preserved legacies of the city's 17th-century Golden Age, and the establishment of the Van Gogh Museum, displaying the work of the famous Dutch modern artist, have attracted millions of visitors to Amsterdam annually.",
        ),
    ]
    batch = d(features)
    expected_decoded_input_ids = [
        "<|prompter|>What are the risks of untreated type 1 diabetes?<|endoftext|>"
        + "<|system|>context: Prolonged lack of insulin can also result in diabetic ketoacidosis, characterized by persistent fatigue, dry or flushed skin, abdominal pain, nausea or vomiting, confusion, trouble breathing, and a fruity breath odor. Blood and urine tests reveal unusually high glucose and ketones in the blood and urine. Untreated ketoacidosis can rapidly progress to loss of consciousness, coma, and death. The percentage of children whose type 1 diabetes begins with an episode of diabetic ketoacidosis varies widely by geography, as low as 15% in parts of Europe and North America, and as high as 80% in the developing world.\n<|endoftext|>"
        + "<|assistant|>Untreated type 1 diabetes can rapidly result in diabetic ketoacidosis which may lead to loss of consciousness, coma and death.<|endoftext|>"
        + 346 * "<|padding|>",
        "<|prompter|>Find all of the Amsterdam museums mentioned in the text and put them in a numbered list.<|endoftext|>"
        + "<|system|>context: Amsterdam's main attractions include its historic canals; the Rijksmuseum, the state museum with a vast collection of Dutch Golden Age art; the Van Gogh Museum; the Dam Square, where the Royal Palace of Amsterdam and former city hall (stadhuis) are located; the Amsterdam Museum; Stedelijk Museum, with modern art; Hermitage Amsterdam, the Concertgebouw concert hall; the Anne Frank House; the Het Scheepvaartmuseum, the Heineken Experience, the Natura Artis Magistra; Hortus Botanicus, NEMO, the red-light district and many cannabis coffee shops. The city is also well known for its nightlife and festival activity; with several of its nightclubs (Melkweg, Paradiso) among the world's most famous. Primarily known for its artistic heritage, elaborate canal system and narrow canal houses with gabled façades; well-preserved legacies of the city's 17th-century Golden Age, and the establishment of the Van Gogh Museum, displaying the work of the famous Dutch modern artist, have attracted millions of visitors to Amsterdam annually.\n<|endoftext|>"
        + "<|assistant|>The Amsterdam museums mentioned in this text are:\n1. Rijksmuseum\n2. Van Gogh Museum\n3. Amsterdam Museum\n4. Stedelijk Museum\n5. Hermitage Amsterdam\n6. Anne Frank House\n7. Het Scheepvaartmuseum\n8. NEMO<|endoftext|>",
    ]
    expected_masked = [
        "<|assistant|>Untreated type 1 diabetes can rapidly result in diabetic ketoacidosis which may lead to loss of consciousness, coma and death.",
        "<|assistant|>The Amsterdam museums mentioned in this text are:\n1. Rijksmuseum\n2. Van Gogh Museum\n3. Amsterdam Museum\n4. Stedelijk Museum\n5. Hermitage Amsterdam\n6. Anne Frank House\n7. Het Scheepvaartmuseum\n8. NEMO",
    ]

    expected_decoded_targets = [
        expected_decoded_input_ids[0][len("<|prompter|>") :] + expected_decoded_input_ids[0][: len("<|prompter|>")],
        expected_decoded_input_ids[1][len("<|prompter|>") :] + expected_decoded_input_ids[1][: len("<|prompter|>")],
    ]
    # this is trivial, since input_ids is a tensor
    assert batch.input_ids[0].shape == batch.input_ids[1].shape
    # since we want to check things in a human readable way
    # we decode the encoded ids back and check if they match the expected text

    assert pythia_tokenizer.decode(batch.input_ids[0]) == expected_decoded_input_ids[0]
    assert pythia_tokenizer.decode(batch.input_ids[1]) == expected_decoded_input_ids[1]

    # check if targets are as expected
    assert pythia_tokenizer.decode(batch.targets[0]) == expected_decoded_targets[0]
    assert pythia_tokenizer.decode(batch.targets[1]) == expected_decoded_targets[1]

    # check if masking is correct. Note that we mask the system as well
    assert pythia_tokenizer.decode(batch.input_ids[0][batch.label_masks[0]]) == expected_masked[0]
    assert pythia_tokenizer.decode(batch.input_ids[1][batch.label_masks[1]]) == expected_masked[1]


def test_dialogue_data_collator(pythia_tokenizer):
    d = DialogueDataCollator(
        tokenizer=pythia_tokenizer,
        padding=True,
    )
    input_features = [
        [
            "When Jada saw the rain outside, she decided to grab her umbrella before leaving the house. She didn't want to get wet, and knew that the umbrella would keep her dry. You are Rain. I don't want to get wet, I'll grab my umbrella.",
            "Hey there! Mind if I talk to you for a bit?",
            "Um, sure I guess.",
            "Great! So, as you can see, it's raining out. Pretty miserable, huh?",
            "Yeah, I was just about to leave and I didn't want to get wet.",
            "Yeah, nobody likes getting wet. But you know what they say, April showers bring May flowers.",
            "I guess that's true.",
            "And speaking of flowers, have you ever seen a rainforest? They're absolutely amazing! Everything is so green and alive.",
            "No, I haven't but it sounds really cool.",
            "Oh, it is! It's one of the most beautiful places on Earth. You should definitely try to see one if you can.",
        ],
        [
            "Kalliope got a bachelor’s degree in English from the University of Michigan. Kalliope has always been interested in writing and literature, so she decided to pursue a degree in English. She worked hard throughout her four years of college and was thrilled to finally receive her diploma. You are Dad. Hey Dad. How are you?",
            "I'm doing well, sweetheart. How's college life treating you?",
            "It's been great so far. I just got my degree in English and I'm looking forward to starting my career soon.",
            "That's terrific! Your mother and I are very proud of you. We know you've worked hard to get where you are today.",
            "Thanks, Dad. I couldn't have done it without your support.",
            "Any time, kiddo. So, what's next for you?",
            "I'm not sure yet. I'm hoping to find a job in publishing or something similar. I just have to start sending out my resume and see what happens.",
            "That sounds like a great plan. I know you'll find the perfect job in no time.",
            "Thanks, Dad. I appreciate your confidence in me.",
        ],
    ]
    batch = d(input_features)
    expected_decoded_input_ids = [
        "<|prompter|>When Jada saw the rain outside, she decided to grab her umbrella before leaving the house. She didn't want to get wet, "
        + "and knew that the umbrella would keep her dry. You are Rain. I don't want to get wet, I'll grab my umbrella.<|endoftext|>"
        + "<|assistant|>Hey there! Mind if I talk to you for a bit?<|endoftext|>"
        + "<|prompter|>Um, sure I guess.<|endoftext|>"
        + "<|assistant|>Great! So, as you can see, it's raining out. Pretty miserable, huh?<|endoftext|>"
        + "<|prompter|>Yeah, I was just about to leave and I didn't want to get wet.<|endoftext|>"
        + "<|assistant|>Yeah, nobody likes getting wet. But you know what they say, April showers bring May flowers.<|endoftext|>"
        + "<|prompter|>I guess that's true.<|endoftext|>"
        + "<|assistant|>And speaking of flowers, have you ever seen a rainforest? They're absolutely amazing! Everything is so green and alive.<|endoftext|>"
        + "<|prompter|>No, I haven't but it sounds really cool.<|endoftext|>"
        + "<|assistant|>Oh, it is! It's one of the most beautiful places on Earth. You should definitely try to see one if you can.<|endoftext|>"
        + 21 * "<|padding|>",
        "<|prompter|>Kalliope got a bachelor’s degree in English from the University of Michigan. Kalliope has always been interested in writing and literature, so she decided to pursue a degree in English. She worked hard throughout her four years of college and was thrilled to finally receive her diploma. You are Dad. Hey Dad. How are you?<|endoftext|>"
        + "<|assistant|>I'm doing well, sweetheart. How's college life treating you?<|endoftext|>"
        + "<|prompter|>It's been great so far. I just got my degree in English and I'm looking forward to starting my career soon.<|endoftext|>"
        + "<|assistant|>That's terrific! Your mother and I are very proud of you. We know you've worked hard to get where you are today.<|endoftext|>"
        + "<|prompter|>Thanks, Dad. I couldn't have done it without your support.<|endoftext|>"
        + "<|assistant|>Any time, kiddo. So, what's next for you?<|endoftext|>"
        + "<|prompter|>I'm not sure yet. I'm hoping to find a job in publishing or something similar. I just have to start sending out my resume and see what happens.<|endoftext|>"
        + "<|assistant|>That sounds like a great plan. I know you'll find the perfect job in no time.<|endoftext|>"
        + "<|prompter|>Thanks, Dad. I appreciate your confidence in me.<|endoftext|>",
    ]
    expected_masked = [
        "<|assistant|>Hey there! Mind if I talk to you for a bit?<|endoftext|>"
        + "<|assistant|>Great! So, as you can see, it's raining out. Pretty miserable, huh?<|endoftext|>"
        + "<|assistant|>Yeah, nobody likes getting wet. But you know what they say, April showers bring May flowers.<|endoftext|>"
        + "<|assistant|>And speaking of flowers, have you ever seen a rainforest? They're absolutely amazing! Everything is so green and alive.<|endoftext|>"
        + "<|assistant|>Oh, it is! It's one of the most beautiful places on Earth. You should definitely try to see one if you can.",
        "<|assistant|>I'm doing well, sweetheart. How's college life treating you?<|endoftext|>"
        + "<|assistant|>That's terrific! Your mother and I are very proud of you. We know you've worked hard to get where you are today.<|endoftext|>"
        + "<|assistant|>Any time, kiddo. So, what's next for you?<|endoftext|>"
        + "<|assistant|>That sounds like a great plan. I know you'll find the perfect job in no time.<|endoftext|>",
    ]
    expected_decoded_targets = [
        # <|prompter|> has 12 tokens, this is removed and added at the end
        expected_decoded_input_ids[0][12:] + expected_decoded_input_ids[0][:12],
        expected_decoded_input_ids[1][12:] + expected_decoded_input_ids[1][:12],
    ]

    # this is trivial, since input_ids is a tensor
    assert batch.input_ids[0].shape == batch.input_ids[1].shape
    # since we want to check things in a human readable way
    # we decode the encoded ids back and check if they match the expected text
    assert pythia_tokenizer.decode(batch.input_ids[0]) == expected_decoded_input_ids[0]
    assert pythia_tokenizer.decode(batch.input_ids[1]) == expected_decoded_input_ids[1]
    # check if the attention mask is correct we mask only the padding
    assert (
        torch.argwhere(batch.attention_mask == 0) == torch.stack([torch.zeros(21), torch.arange(217, 238)], dim=1)
    ).all()
    assert (
        torch.argwhere(batch.attention_mask == 1)
        == torch.cat(
            [
                torch.stack([torch.zeros(217), torch.arange(0, 217)], dim=1),
                torch.stack([torch.ones(238), torch.arange(0, 238)], dim=1),
            ]
        )
    ).all()
    # Check that the attention mask is only applied to padding tokens
    padding_token = pythia_tokenizer.get_vocab()[pythia_tokenizer.pad_token]
    assert (torch.argwhere(batch.attention_mask == 0) == torch.argwhere(batch.input_ids == padding_token)).all()
    # check if the masking works correctly, we mask everything between <|assistant|> and <|endoftext|>
    # todo: we mask the last <|endoftext|> but I don't see a reason why???
    assert pythia_tokenizer.decode(batch.input_ids[0][batch.label_masks[0]]) == expected_masked[0]
    assert pythia_tokenizer.decode(batch.input_ids[1][batch.label_masks[1]]) == expected_masked[1]

    # check if targets are as expected
    assert pythia_tokenizer.decode(batch.targets[0]) == expected_decoded_targets[0]
    assert pythia_tokenizer.decode(batch.targets[1]) == expected_decoded_targets[1]
