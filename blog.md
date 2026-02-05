---
layout: default
title: "Blog"
description: My random thoughts, musings, and technical side projects.
---
<div class="post">
<h1>{{ page.title }}</h1>
<p>{{ page.description }}</p>
<ul>
{% assign blog_posts = site.tags.blog %}
{% for post in blog_posts %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
