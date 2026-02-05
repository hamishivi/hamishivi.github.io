---
layout: default
permalink: /classics
---
<div class="post">
<h1>Classics</h1>
<p>Posts about classical languages and ancient history.</p>
<ul>
{% for post in site.tags.classics %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    ({{ post.date | date_to_string }}){% for tag in post.tags %}{% unless tag == "blog" %} <a href="/{{ tag }}" class="post-tag">{{ tag }}</a>{% endunless %}{% endfor %}<br>
    <p class="post-meta">{{ post.description }}</p>
  </li>
{% endfor %}
</ul>
</div>
<hr>
