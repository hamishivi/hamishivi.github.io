---
layout: default
permalink: /technical
---
<div class="post">
<h1>Technical</h1>
<p>My technical side projects, often involving live code demos and descriptions of what I've done.</p>
<ul>
{% for post in site.tags.technical %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
