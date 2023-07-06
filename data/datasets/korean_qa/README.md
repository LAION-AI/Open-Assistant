# Korean QA Dataset

https://huggingface.co/datasets/CertifiedJoon/Korean-Instruction

This repository contains the Python code used to generate the `Korean QA`
dataset. `Korean QA` is a dataset designed to evaluate the ability of models to
perform question answering in korean natural language.

The dataset contains 1.74k instruction and answers, all of which are from Naver
Kin, the number one QNA website in korea.

## Dataset Structure

[Instruction, Response, Source, Metadata]

## Data Acquisition Strategy

I have employed a web crawler designed specifically for Naver Kin to extract
instruction and answer from webpages. As well, I have completed mannual clean up
to remove unnecessary and meaningless data.
