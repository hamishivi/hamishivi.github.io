---
layout: default
permalink: /nlp
---
<div class="post">
<h1>NLP</h1>
<p>Posts about natural language processing.</p>
<ul>
{% for post in site.tags.nlp %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
