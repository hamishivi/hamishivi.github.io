---
layout: default
permalink: /personal
---
<div class="post">
<h1>Personal</h1>
<p>Personal reflections and media consumption lists.</p>
<ul>
{% for post in site.tags.personal %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
