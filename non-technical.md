---
layout: default
permalink: /non-technical
title: Non-technical
description: Thoughts and reflections on books, films, games, and other interests.
---
<div class="post">
<h1>Non-technical</h1>
<p>My random thoughts and musings on various things I've read or played recently.</p>
<ul>
{% for post in site.tags.non-technical %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
