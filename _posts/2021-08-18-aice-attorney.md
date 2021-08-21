---
layout: post
title: AI-ce Attorney
tags: blog technical
description: I made a fun little animated Ace Attorney AI script generator.
---

> tl;dr: [check out a fun little Ace Attorney generator I made!](https://share.streamlit.io/hamishivi/aice-attorney)

*[Phoenix Wright: Ace Attorney](https://en.wikipedia.org/wiki/Ace_Attorney)* is a visual novel series created by Shu Takumi (also of *[Ghost Trick](https://en.wikipedia.org/wiki/Ghost_Trick:_Phantom_Detective)* fame) where you play as a lawyer (usually the titular character Phoenix Wright, although this changes over the games) in a heavily fictionalised version of the Japanese legal system. I heavily recommend this series if you like murder mysteries or puzzle games - the gameplay loop is centred around investigating murders and finding evidence, and then using that evidence in court to prove contradictions or lies in witness' testimonies.



As a visual novel, *Ace Attorney* is a text-heavy game, and so with the recent release of the *[Great Ace Attorney Chronicles](https://www.ace-attorney.com/great1-2/en-asia/)* and the popularity of the [twitter court bot](https://twitter.com/acecourtbot2?lang=en), I thought it would be fun to make use of the court bot's code to auto-generate *Ace Attorney* scripts and animate them! This is fairly easy to do, as it turns out - I used the great [aitextgen](https://docs.aitextgen.io/) library for training models and generating text, and the [objection engine library](https://github.com/LuisMayo/objection_engine) for animating the scripts - all I had to do really was train the model itself and write some code to convert it to a format the objection engine recognises.



I made this into a little [streamlit](https://streamlit.io/) app available [here](https://share.streamlit.io/hamishivi/aice-attorney) using the [125M GPT-neo](https://huggingface.co/EleutherAI/gpt-neo-125M) model (in order to keep processing times reasonably fast), so check it out! And if you find yourself enjoying the scenarios, I definitely recommend checking out any of the *Ace Attorney* games.



> 🚨 It's important to note that I'm not filtering the bot, so it could produce potentially harmful text. *Ace Attorney* is mostly a teen-rated game, so there shouldn't be much worse than murder mystery discussions, but the original training data of GPT-neo was much wider and expansive, so be warned!
