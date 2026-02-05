---
layout: default
permalink: /games
---
<div class="post">
<h1>Games</h1>
<p>Posts about video games and game AI.</p>
<ul>
{% for post in site.tags.games %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
