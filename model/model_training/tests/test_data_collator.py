
from custom_datasets.dialogue_collator import DialogueDataCollator
from transformers.models.auto.tokenization_auto import get_tokenizer_config, AutoTokenizer
from model_training.utils import match_tokenizer_name

def test_dialogue_data_collator():
    import pdb; pdb.set_trace()
    tokenizer = AutoTokenizer.from_pretrained("tests/resources/data_collator", local_files_only=True)
    tokenizer_config = match_tokenizer_name("pythia")

    tokenizer.add_special_tokens(
        {
            "pad_token": tokenizer_config.special_tokens.pad_token,
            "eos_token": tokenizer_config.special_tokens.eos_token,
            "sep_token": tokenizer_config.special_tokens.sep_token,
        }
    )
    # tokenizer_config = get_tokenizer_config("tests/resources/data_collator", cache_dir="tests/resources/data_collator", local_files_only=True)
    import pdb; pdb.set_trace()

    d = DialogueDataCollator(
        tokenizer=tokenizer,
        padding=True,
        # max_length=256,
        # max_length_threshold=256,
        # pad_to_multiple_of=256,
    )
    input_features = [["When Jada saw the rain outside, she decided to grab her umbrella before leaving the house. She didn't want to get wet, and knew that the umbrella would keep her dry. You are Rain. I don't want to get wet, I'll grab my umbrella.", 
                       "Hey there! Mind if I talk to you for a bit?", 
                       "Um, sure I guess.", 
                       "Great! So, as you can see, it's raining out. Pretty miserable, huh?", 
                       "Yeah, I was just about to leave and I didn't want to get wet.", 
                       "Yeah, nobody likes getting wet. But you know what they say, April showers bring May flowers.", 
                       "I guess that's true.", 
                       "And speaking of flowers, have you ever seen a rainforest? They're absolutely amazing! Everything is so green and alive.", 
                       "No, I haven't but it sounds really cool.", 
                       "Oh, it is! It's one of the most beautiful places on Earth. You should definitely try to see one if you can."], 
                       ["Kalliope got a bachelor’s degree in English from the University of Michigan. Kalliope has always been interested in writing and literature, so she decided to pursue a degree in English. She worked hard throughout her four years of college and was thrilled to finally receive her diploma. You are Dad. Hey Dad. How are you?", 
                        "I'm doing well, sweetheart. How's college life treating you?", "It's been great so far. I just got my degree in English and I'm looking forward to starting my career soon.", 
                        "That's terrific! Your mother and I are very proud of you. We know you've worked hard to get where you are today.", 
                        "Thanks, Dad. I couldn't have done it without your support.", 
                        "Any time, kiddo. So, what's next for you?", 
                        "I'm not sure yet. I'm hoping to find a job in publishing or something similar. I just have to start sending out my resume and see what happens.", 
                        "That sounds like a great plan. I know you'll find the perfect job in no time.", 
                        "Thanks, Dad. I appreciate your confidence in me."]
                      ]
    import pdb; pdb.set_trace()
    batch = d(input_features)
    # test_strings = "<|prompter|>When Jada saw the rain outside, she decided to grab her umbrella before leaving the house. She didn"t want to get wet, and knew that the umbrella would keep her dry. You are Rain. I don"t want to get wet, I"ll grab my umbrella.<|endoftext|><|assistant|>Hey there! Mind if I talk to you for a bit?<|endoftext|><|prompter|>Um, sure I guess.<|endoftext|><|assistant|>Great! So, as you can see, it"s raining out. Pretty miserable, huh?<|endoftext|><|prompter|>Yeah, I was just about to leave and I didn"t want to get wet.<|endoftext|><|assistant|>Yeah, nobody likes getting wet. But you know what they say, April showers bring May flowers.<|endoftext|><|prompter|>I guess that"s true.<|endoftext|><|assistant|>And speaking of flowers, have you ever seen a rainforest? They"re absolutely amazing! Everything is so green and alive.<|endoftext|><|prompter|>No, I haven"t but it sounds really cool.<|endoftext|><|assistant|>Oh, it is! It"s one of the most beautiful places on Earth. You should definitely try to see one if you can.<|endoftext|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|>"
    # test_strings2 = "<|prompter|>Kalliope got a bachelor’s degree in English from the University of Michigan. Kalliope has always been interested in writing and literature, so she decided to pursue a degree in English. She worked hard throughout her four years of college and was thrilled to finally receive her diploma. You are Dad. Hey Dad. How are you?<|endoftext|><|assistant|>I"m doing well, sweetheart. How"s college life treating you?<|endoftext|><|prompter|>It"s been great so far. I just got my degree in English and I"m looking forward to starting my career soon.<|endoftext|><|assistant|>That"s terrific! Your mother and I are very proud of you. We know you"ve worked hard to get where you are today.<|endoftext|><|prompter|>Thanks, Dad. I couldn"t have done it without your support.<|endoftext|><|assistant|>Any time, kiddo. So, what"s next for you?<|endoftext|><|prompter|>I"m not sure yet. I"m hoping to find a job in publishing or something similar. I just have to start sending out my resume and see what happens.<|endoftext|><|assistant|>That sounds like a great plan. I know you"ll find the perfect job in no time.<|endoftext|><|prompter|>Thanks, Dad. I appreciate your confidence in me.<|endoftext|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|><|padding|>""

    # """
    # Expects a list of texts corresponding to a sequence of [question, answer, question, answer, ...] pairs.
    # """

    # tokenizer: PreTrainedTokenizerBase
    # padding: Union[bool, str, PaddingStrategy] = True
    # max_length: Optional[int] = None
    # mix_length_threshold: Optional[int] = 256
    # mix_probability: Optional[float] = 0.6
    # pad_to_multiple_of: Optional[int] = None
    # samples_mixing: Optional[bool] = False
    # random_offset_probability: Optional[float] = 0.5
    # label_masking: bool = True
    # use_system_prefix: bool = False
    # system_prefix: str = None
    # self.tokenizer.decode(batch.input_ids[0])
    # self.tokenizer.decode(batch.input_ids[0][batch.label_masks[0]])
    # self.tokenizer.decode(batch.input_ids[0][batch.label_masks[0]])
    # self.tokenizer.decode(batch.input_ids[batch.label_masks])
    # self.tokenizer.decode(torch.where(batch.attention_mask[0].eq(1), batch.input_ids[0], batch.attention_mask[0]))

    # todo: how to get a MINIMAL tokenizer??? -> check how to get the relevant tokens in our text and limit the tokenizer only to that