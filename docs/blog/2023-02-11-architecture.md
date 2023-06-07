---
title: The Architecture so Far!
description: This is the architecture of our app so far.
slug: 2023-02-11-architecture
authors: AbdBarho
tags: [open-assistant]
---

I thought it would make sense to document our architecture as a blog post, since
it would be easily visible for everyone, and it would also be nice to look back
a couple months from now and see how stuff has changed :)

A lot of work was done in the past couple of week to establish the needed
infrastructure both for data collection and inference purposes. Thanks to
everyone, and especially community members who supported us so far!

Our current plan for the architecture of the Open Assistant is as follows:

```mermaid
flowchart TD
  subgraph next[Web Frontend]
    direction TB
    website([Browser]) & nextbackend[Backend] & webpostgres[(PostgreSQL)]
  end

  subgraph data[Python backend]
    direction TB
    backend[Backend] & postgres[(PostgreSQL)] & redis[(Redis)]
  end

  subgraph inference[Inference Service]
    direction TB
    inferenceServer[Server] -.- infpostgres[(PostgreSQL)]
  end

  subgraph workers[Inference Workers]
    direction TB
    worker1[Worker] --- textgen1[Text\ngenerator]
    worker2[Worker] --- textgen2[Text\ngenerator]
    worker3[Worker] --- textgen3[Text\ngenerator]
  end

  website --> nextbackend
  nextbackend -.- webpostgres

  next --- data

  backend -.- postgres & redis

  next --- inference

  inference --- workers
```

We are working on setting up the inference as shown above, and considering our
options for hosting, also, we want to move our authentication from the website
to the python backend.

Of course, this is by no means final, and lot of questions are still open, and
that is the fun of it! If you want to join us on our journey, just give our
[github](https://github.com/LAION-AI/Open-Assistant) a look!
