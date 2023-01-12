# This notebook will run on a system with a single RTX3090 (24 GB vram).
# You need to install accelerate, bitsandbytes, and transformers

import math
import pickle
import time

import torch

# load all needed libraries
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# This device map will work a GPU with > 24GB vram.
# It uses nearly all the memory.
device_map_T5_13B = {
    "shared": 0,
    "decoder.embed_tokens": 0,
    "encoder.embed_tokens": 0,
    "encoder.block.0": 0,
    "encoder.block.1": 0,
    "encoder.block.2": 0,
    "encoder.block.3": 0,
    "encoder.block.4": 0,
    "encoder.block.5": 0,
    "encoder.block.6": 0,
    "encoder.block.7": 0,
    "encoder.block.8": 0,
    "encoder.block.9": 0,
    "encoder.block.10": 0,
    "encoder.block.11": 0,
    "encoder.block.12": 0,
    "encoder.block.13": 0,
    "encoder.block.14": 0,
    "encoder.block.15": 0,
    "encoder.block.16": 0,
    "encoder.block.17": 0,
    "encoder.block.18": 0,
    "encoder.block.19": 0,
    "encoder.block.20": 0,
    "encoder.block.21": 0,
    "encoder.block.22": 0,
    "encoder.block.23": 0,
    "encoder.final_layer_norm": 0,
    "encoder.dropout": 0,
    "decoder.block.0": 0,
    "decoder.block.1": 0,
    "decoder.block.2": 0,
    "decoder.block.3": 0,
    "decoder.block.4": 0,
    "decoder.block.5": 0,
    "decoder.block.6": 0,
    "decoder.block.7": 0,
    "decoder.block.8": 0,
    "decoder.block.9": 0,
    "decoder.block.10": 0,
    "decoder.block.11": 0,
    "decoder.block.12": 0,
    "decoder.block.13": 0,
    "decoder.block.14": 0,
    "decoder.block.15": 0,
    "decoder.block.16": 0,
    "decoder.block.17": 0,
    "decoder.block.18": 0,
    "decoder.block.19": 0,
    "decoder.block.20": 0,
    "decoder.block.21": 0,
    "decoder.block.22": 0,
    "decoder.block.23": 0,
    "decoder.final_layer_norm": 0,
    "decoder.dropout": 0,
    "lm_head": 0,
}


# Load the model in bfloat16. Make sure to use bfloat16
# if you are doing inference with 16bit precision.
tokenizer = AutoTokenizer.from_pretrained("flan-t5-xxl")
model = AutoModelForSeq2SeqLM.from_pretrained(
    "flan-t5-xxl",
    device_map=device_map_T5_13B,
    torch_dtype=torch.bfloat16,
    load_in_8bit=False,
)


# Load strings as knowledge sources for QA generation.
# You can do this with a pickle.
objects = []
with (open("paragraphs.pkl", "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
paragraphs = objects[0]

# Make sure no paragraphs are too long for T5.
# It handles up to 512 tokens context length.
fixed_paragraphs = []
for k in paragraphs:
    if len(k) > 1100:
        pass
    else:
        fixed_paragraphs.append(k)
print("Original number of paragraphs:", len(paragraphs))
print("Length filtered number of paragraphs:", len(fixed_paragraphs))
paragraphs = fixed_paragraphs


# Sort_Tuple sorts a list of tuples
# by the second element.
def Sort_Tuple(tup):
    tup.sort(key=lambda x: x[1], reverse=True)
    return tup


# ask_flan_T5 takes a text input and returns the
# response of FLAN_T5 and a normalized logits
# score for the generation.
def ask_flan_T5(input_text):
    inputs = tokenizer.encode(input_text, return_tensors="pt").cuda(0)
    outputs = model.generate(
        inputs,
        do_sample=True,
        top_p=0.95,
        eos_token_id=1,
        max_new_tokens=50,
        bos_token_id=0,
        temperature=0.9,
        return_dict_in_generate=True,
        output_scores=True,
    )
    out_text = tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)
    probs = torch.stack(outputs.scores, dim=1).softmax(-1)
    for i in outputs.sequences:
        logprobs = 0
        counter = 0
        for k in i[1:]:
            word_prob = (round(probs[0][counter][k.item()].item(), 2)) + 0.001
            logprobs = logprobs + math.log(word_prob)
            counter += 1
        out_tuple = (out_text, round(logprobs, 2))
    return out_tuple


# ask_flan_T5D is a function that takes an input text and
# returns the deterministic(do_sample=False) output of
# FLAN_T5 and logits.
def ask_flan_T5D(input_text):
    inputs = tokenizer.encode(input_text, return_tensors="pt").cuda(0)
    outputs = model.generate(
        inputs,
        do_sample=False,
        eos_token_id=1,
        max_new_tokens=50,
        bos_token_id=0,
        return_dict_in_generate=True,
        output_scores=True,
    )
    out_text = tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)
    probs = torch.stack(outputs.scores, dim=1).softmax(-1)
    for i in outputs.sequences:
        logprobs = 0
        counter = 0
        for k in i[1:]:
            word_prob = (round(probs[0][counter][k.item()].item(), 2)) + 0.001
            logprobs = logprobs + math.log(word_prob)
            counter += 1
        out_tuple = (out_text, round(logprobs, 2))
    return out_tuple


# Generate a topic classifier for a paragraph of text
def generate_topic(paragraph):
    results = set()
    input_text = (
        "Task: Create a topic classifier for the provided \
        paragraph.\nParagraph:\n"
        + paragraph
        + "\nTopic: "
    )
    for k in range(0, 20):
        result = ask_flan_T5(input_text)
        if result[1] > -4:
            results.add(result)
        if len(results) < 3:
            results.add(("I was wondering", -3.3))
            results.add(("I have a question", -3.3))
    sorted_results = Sort_Tuple(list(results))
    return sorted_results[0:5]


# Generate a topic classifier for a paragraph of text
def generate_topic_prefix(topic_set):
    results = set()
    for entry in topic_set:
        topic = entry[0]
        input_text = (
            "Task: Create a prepositional phrase about the topic.\n\
            Example 1\n Topic: climbing mount everest\nPrepositional \
            Phrase: With regards to climbing mount everest,\nExample \
            2\nTopic: United States Air Force\nPrepositional Phrase: \
            On the topic of the United States Air Force,\n Example 3\nTopic: "
            + topic
            + "\nPrepositional Phrase: "
        )
        for k in range(0, 5):
            results.add(ask_flan_T5(input_text))
        sorted_results = Sort_Tuple(list(results))
        return sorted_results[0:5]


# Generate who/what/where/when/why questions from a paragraph.
# Number of questions variable is an integer which indicates how
# many of each question type to try to generate.
def generate_questions(paragraph, number_of_questions):
    if len(tokenizer.encode(paragraph)) > 480:
        print("Warning, the context length is too long.")
    question_set = set()
    question_types = [
        "What",
        "Where",
        "Why",
        "How",
        "Who",
    ]
    for qtype in question_types:
        question = (
            "Please generate a question that starts with '"
            + qtype
            + "' based on the following paragraph.\nText:\n"
            + paragraph
            + "\nQuestion:\n"
        )
        for k in range(0, number_of_questions):
            new_question = ask_flan_T5(question)
            if qtype in new_question[0]:
                question_set.add((qtype, new_question))
    return question_set


# Generate answers for a set of questions.
# Input is the paragraph of text and a set of questions where each question
# is a tuple generated from the generate_questions() function.
def generate_answers(paragraph, question_set):
    possible_answers = set()
    for question in question_set:
        input_text = (
            "Please read the following paragraph and \
            then answer the question using only data \
            found in the text. If no answer is possible, respond \
            'NA'.\nText:\n"
            + paragraph
            + "\nQuestion:\n"
            + question[1][0]
            + "\nAnswer:\n"
        )
        answer = ask_flan_T5D(input_text)
        if "NA" in answer[0]:
            pass
        else:
            possible_answers.add((question[0], question[1], answer))
    return possible_answers


# Generate questions from a paragraph and set of answers.
# Input is the paragraph of text and a set of answers where each question
# is a tuple generated from the generate_answers() function.
def generate_question2(paragraph, qa_set):
    qaq_results = set()
    for qa_item in qa_set:
        answer = qa_item[2][0]
        input_text = (
            "Please read the following paragraph and \
            then generate a question whose answer is: "
            + answer
            + "\nParagraph:\n"
            + paragraph
            + "\nQuestion:\n"
        )
        result = ask_flan_T5D(input_text)
        qaq_results.add((qa_item[0], qa_item[1], qa_item[2], result))
    return qaq_results


# Generate answers from a paragraph and set of questions.
# Input is the paragraph of text and a set of questions where each answer
#  is a tuple generated from the generate_questions2() function.
def generate_answers2(paragraph, question_set):
    possible_answers = set()
    for question in question_set:
        input_text = (
            "Please read the following paragraph and \
            then answer the question using only data \
            found in the text. If no answer is possible, respond \
            'NA'.\nText:\n"
            + paragraph
            + "\nQuestion:\n"
            + question
            + "\nAnswer:\n"
        )
        answer = ask_flan_T5D(input_text)
        possible_answers.add((question, answer))
    return possible_answers


# Generate declarative statement from question and answer pair.
def generate_declarative(qaq_set):
    qaqd_results = set()
    for qa_item in qaq_set:
        question = qa_item[0]
        answer = qa_item[1][0]
        if "NA" in answer:
            pass
        else:
            input_text = (
                "Generate a declarative statement based on the \
                given question and answer pair.\nQ: What is \
                sitting on the couch?\nA: poodle\nA poodle is \
                sitting on the couch.\nQ: "
                + question
                + "\nA: "
                + answer
                + "\n"
            )
            result = ask_flan_T5D(input_text)
            qaqd_results.add((question, answer, result))
    return qaqd_results


# Generate closed book answer to question.
def generate_closed_answer(qaqd_set):
    qaqd_results = set()
    for qa_item in qaqd_set:
        question = qa_item[0]
        answer = qa_item[2][0]
        if "NA" in answer:
            # print(answer)
            pass
        else:
            input_text = (
                "Task: Answer the question in a detailed fashion. \
                If the question cannot be answered without more \
                information, please answer NA.\nExample 1:\nQuestion: \
                Why does Shala like cookies?\nAnswer: It is not possible \
                to know why Shala likes cookies without more information, \
                but many people that like cookies enjoy their taste or \
                some of their ingredients (e.g. chocolate chips or \
                peanut butter).\nExample 2:\nQuestion: Why would someone \
                vote in an election?\nAnswer: There are many reasons \
                someone might vote in an election, for instance to have \
                their voice heard or to help a candidate they like win the \
                race.\nExample 3\nQuestion: What decoration goes on top of \
                a Christmas tree?\nAnswer: Usually a star is placed at the \
                top of a Christmas tree.\nExample 4:\nQuestion: "
                + question
                + "\nAnswer: "
            )
            result = ask_flan_T5D(input_text)
            qaqd_results.add((qa_item[0], qa_item[1], qa_item[2], result))
    return qaqd_results


# Create a dictionary of questions and answers from a list of paragraphs.
# Takes about 20 seconds per paragraph to process.
start_time = time.perf_counter()
questions_dict = {}
uniq_id = 100000
for paragraph in paragraphs[0:1500]:
    topic_list = generate_topic(paragraph)
    topic_prefix = generate_topic_prefix(topic_list)
    question_set = generate_questions(paragraph, 2)
    qa_set = generate_answers(paragraph, question_set)
    qaq_set = generate_question2(paragraph, qa_set)
    q2_set = set()
    for q in qaq_set:
        q2_set.add(q[3][0])
    q2a2_set = generate_answers2(paragraph, q2_set)
    a2d_set = generate_declarative(q2a2_set)
    a3cb_set = generate_closed_answer(a2d_set)
    questions_dict[uniq_id] = {}
    questions_dict[uniq_id]["topics"] = topic_list
    questions_dict[uniq_id]["topic prepositions"] = topic_prefix
    questions_dict[uniq_id]["paragraph"] = paragraph
    entry_count = 0
    entry_dict = {}
    for entry in a3cb_set:
        entry_dict[entry_count] = {}
        entry_dict[entry_count]["question"] = entry[0]
        entry_dict[entry_count]["answer_T5_ob"] = entry[2][0]
        entry_dict[entry_count]["answer_T5_cb"] = entry[3][0]
        entry_count += 1
    questions_dict[uniq_id]["QA_set"] = entry_dict
    uniq_id += 1
    print(uniq_id, "topics:", topic_prefix)

stop_time = time.perf_counter()
generation_time = stop_time - start_time
print(questions_dict[uniq_id - 1])
print(generation_time)


# create a binary pickle file to save your dictionary
f = open("questions_dict.pkl", "wb")
pickle.dump(questions_dict, f)
f.close()
