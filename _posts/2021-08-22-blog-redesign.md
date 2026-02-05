---
layout: post
title: Blog Redesign
tags: blog technical web
description: A quick go-over of my recent blog changes.
---

As a quick note, I've recently done a go-over of the design of my blog. In this post, I'm just going to go over the changes and how my blog setup currently works. I won't go too deep into details as my setup largely follows the standard [Github Pages](https://pages.github.com/) and [Jekyll](https://jekyllrb.com/) setup.

I'm using the default [Minima](https://github.com/jekyll/minima) theme, considering it's both simple and fairly easy to modify. These are currently the various things I've added to it (beyond general style tweaks):

- A light-dark mode toggle, utilising Google Chrome Lab's [`dark-mode-toggle`](https://github.com/GoogleChromeLabs/dark-mode-toggle) element
- A tag system, based on [Long Qian's guide](http://longqian.me/2017/02/09/github-jekyll-tag/), which I also use to split my posts into the 'side projects' and 'random' sections above.

As I tweak the plugins and design, I'll come back to this post and add my changes to the list above. Hopefully, it provides a useful list of ways to tweak a Github Pages site to your liking (and remind me of what I added if I chose to change it up again). Alternatively, you can find the codebase for this site [here](https://github.com/hamishivi/hamishivi.github.io).