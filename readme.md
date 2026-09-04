# Hamish's site

A Jekyll site deployed to GitHub Pages by GitHub Actions. The workflow builds the site itself so Jekyll Scholar works on Pages. Layouts and styles live in this repository; the page shell and social icons retain their Minima license in `assets/minima-LICENSE.txt`.

## Local development

Install the Ruby version in `.ruby-version`, then run:

```sh
bundle install
bundle exec jekyll serve
```

For a production build and the same checks used in CI:

```sh
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
python3 scripts/check_site.py _site
```

Pull requests build and validate the site. Only pushes to `master` or manual runs on `master` deploy to GitHub Pages. Repository Pages settings should use **GitHub Actions** as the source.

## Writing

- Put posts in `_posts/YYYY-MM-DD-slug.md`, with `layout: post`, a title, description, and tags. Include the `blog` tag to appear in the main archive.
- Set `mathjax: true` only for posts with equations.
- Article images live in the Cloudflare R2 bucket `ivison-site-images`, served from `https://images.ivison.id.au`. Upload images through the bucket's **Objects → Upload** control; image files do not need to be committed to this repository. Use descriptive, versioned filenames when replacing an image so cached copies cannot become stale.
- Add descriptive `alt` text, intrinsic `width` and `height`, and `loading="lazy"` to article images. CSS preserves the aspect ratio and fits images to the screen. Use a CSS width when a figure should be smaller than its intrinsic size.
- Topic pages use `_layouts/tag_page.html`; both archive views share `_includes/post_card.html`.
- Add papers to `_bibliography/references.bib`. Publication years are generated from `scholar.first_year` through the current year, skipping empty years; the latest two years start expanded.
- Theme colors are paired with CSS `light-dark()` in `assets/css/site.css`. The header toggle saves an override; without one, the theme follows the system preference.

`scripts/`, this README, and other development files are excluded from the published artifact. The old Notion converter and Imgur upload helper have been retired.
