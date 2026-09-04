---
layout: home
description: Research, publications, and writing from Hamish Ivison, a University of Washington PhD student working on language-model post-training and reinforcement learning.
image: /assets/static/me-400.jpg
---

Hi, I'm <span class="pronunciation"><button class="pronunciation-trigger" type="button" aria-label="Hamish, pronounced HAY-mish" aria-expanded="false">Hamish</button><span class="pronunciation-tooltip" aria-hidden="true">[ˈheɪmɪʃ]</span></span>! I'm a PhD student in the University of Washington's [H2Lab](https://h2lab.cs.washington.edu/), advised by [Hannaneh Hajishirzi](https://homes.cs.washington.edu/~hannaneh/), and a student researcher at Google DeepMind. My research focuses on post-training for language models: making them more useful to more people, improving them beyond next-token prediction (especially with reinforcement learning), and understanding better data mixtures. I also dabble in alternative approaches to language modelling.

I'm from Sydney and completed my undergraduate studies at the University of Sydney, earning degrees in Arts and IT with majors in Linguistics, Classical Greek, and Computer Science. I also worked with the university's natural language processing group on multi-hop question answering. During and just after my undergraduate studies, I spent time at the [Commonwealth Bank of Australia](https://www.commbank.com.au/), a few startups, and [Optiver](https://www.optiver.com/). Before my PhD, I was a predoctoral researcher at [AI2](https://allenai.org/) on the [AllenNLP team](https://github.com/allenai/allennlp).

If you have questions about my work, academia, software, or research—or just want to chat—feel free to reach out at hamishiv [at] cs [dot] washington [dot] edu. I'm generally happy to answer questions. You can also find me as [@hamishivi](https://x.com/hamishivi).

<hr>
<h2>Papers</h2>

See below for papers I've worked on. You can also check out my [Semantic Scholar](https://www.semanticscholar.org/author/Hamish-Ivison/2056776606) and [Google Scholar](https://scholar.google.com/citations?user=JxCXMlkAAAAJ) profiles.

<div class="publication-tools publication-actions" aria-label="Publication display controls">
    <button id="expand-publications" class="utility-button" type="button">Expand all years</button>
    <button id="collapse-publications" class="utility-button" type="button">Collapse all years</button>
</div>

{% assign latest_year = site.time | date: '%Y' | plus: 0 %}
{% assign expanded_since = latest_year | minus: 1 %}
{% for year in (site.scholar.first_year..latest_year) reversed %}
  {% capture publication_count %}{% bibliography_count --query @*[year={{year}}] %}{% endcapture %}
  {% assign publication_count = publication_count | plus: 0 %}
  {% if publication_count > 0 %}
<details class="year-section" id="year-{{ year }}"{% if year >= expanded_since %} open{% endif %}>
  <summary class="year-toggle">{{ year }}</summary>
  <div class="year-content">
    {% bibliography --query @*[year={{year}}] %}
  </div>
</details>
  {% endif %}
{% endfor %}
