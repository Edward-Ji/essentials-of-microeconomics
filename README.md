---
title: Essentials of Microeconomics
emoji: 💸
colorFrom: yellow
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# Essentials of Microeconomics

[![Hugging Face][hf-badge]][hf-space]

This repository contains code for demonstrating some concepts in _Essentials of
Microeconomics_ - a textbook by Andrew Wait and Bonnie Nguyen.

## Run locally

Install dependencies using `pip`:

```
pip install -r requirements.txt
```

Run the following command to start the shiny app:

```
shiny run --reload essentials_of_microeconomics/app.py
```

Open the link in the output (typically http://127.0.0.1:8000) in a browser.

[hf-badge]: https://img.shields.io/badge/%F0%9F%A4%97-Hugging_Face-f59e0b?style=for-the-badge&logo=hf
[hf-space]: https://huggingface.co/spaces/Edward-Ji/essentials-of-microeconomics
