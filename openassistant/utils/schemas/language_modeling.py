# -*- coding: utf-8 -*-
"""
Language Modeling Schema
"""
import datasets

features = datasets.Features(
    {
        "text": datasets.Value("string"),
        "meta": [datasets.Value("string")],
    }
)
