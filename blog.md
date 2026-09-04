---
layout: default
title: "Blog"
description: My random thoughts, musings, and technical side projects.
---
<div class="post">
<h1>{{ page.title }}</h1>
<p>{{ page.description }}</p>

<div class="archive-tools">
  <p class="filter-label" id="topic-filter-label">Filter by topic</p>
  <div class="tag-filters" role="group" aria-labelledby="topic-filter-label">
    <button class="filter-chip is-active" type="button" data-tag="all" aria-pressed="true">All</button>
    {% assign sorted_tags = site.tags | sort %}
    {% for tag in sorted_tags %}
      {% assign tag_name = tag[0] %}
      {% unless tag_name == "blog" %}
        <button class="filter-chip" type="button" data-tag="{{ tag_name | escape }}" aria-pressed="false">{{ tag_name }}</button>
      {% endunless %}
    {% endfor %}
  </div>
  <p id="post-filter-status" class="filter-status" aria-live="polite"></p>
</div>

<ul id="post-list" class="post-list filterable-post-list">
{% assign blog_posts = site.tags.blog %}
{% for post in blog_posts %}
  <li class="post-list-item" data-tags="{{ post.tags | join: ' ' | escape }}">
    {% include post_card.html post=post %}
  </li>
{% endfor %}
</ul>
</div>
<hr>
