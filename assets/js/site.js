document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('theme-toggle');
    const root = document.documentElement;

    function updateThemeToggle() {
      if (!toggle) return;
      const isDark = root.getAttribute('data-theme') === 'dark';
      toggle.setAttribute('aria-pressed', String(isDark));
      toggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }

    if (toggle) {
      updateThemeToggle();
      toggle.addEventListener('click', function() {
        const theme = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', theme);
        try {
          localStorage.setItem('theme', theme);
        } catch (error) {}
        updateThemeToggle();
      });
    }

    const systemTheme = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
    if (systemTheme) {
      systemTheme.addEventListener('change', function(event) {
        let savedTheme = null;
        try {
          savedTheme = localStorage.getItem('theme');
        } catch (error) {}
        if (!savedTheme) {
          root.setAttribute('data-theme', event.matches ? 'dark' : 'light');
          updateThemeToggle();
        }
      });
    }

    document.querySelectorAll('.pronunciation').forEach(function(wrapper) {
      const trigger = wrapper.querySelector('.pronunciation-trigger');
      if (!trigger) return;

      function setPronunciationOpen(open) {
        wrapper.classList.toggle('is-open', open);
        wrapper.classList.toggle('is-dismissed', !open);
        trigger.setAttribute('aria-expanded', String(open));
      }

      trigger.addEventListener('click', function() {
        setPronunciationOpen(!wrapper.classList.contains('is-open'));
      });

      trigger.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
          event.preventDefault();
          setPronunciationOpen(false);
        }
      });

      trigger.addEventListener('blur', function() {
        wrapper.classList.remove('is-open', 'is-dismissed');
        trigger.setAttribute('aria-expanded', 'false');
      });

      wrapper.addEventListener('mouseleave', function() {
        wrapper.classList.remove('is-open', 'is-dismissed');
        trigger.setAttribute('aria-expanded', 'false');
      });
    });

    const detailButtons = Array.from(document.querySelectorAll('.publication-toggle'));
    detailButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        const shouldOpen = this.getAttribute('aria-expanded') !== 'true';
        detailButtons.forEach(function(other) {
          const expanded = other === button && shouldOpen;
          other.setAttribute('aria-expanded', String(expanded));
          document.getElementById(other.getAttribute('aria-controls')).hidden = !expanded;
        });
      });
    });

    function copyText(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text);
      }

      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();

      const copied = document.execCommand('copy');
      textarea.remove();
      return copied ? Promise.resolve() : Promise.reject(new Error('Copy failed'));
    }

    document.querySelectorAll('.copy-bibtex').forEach(function(button) {
      button.addEventListener('click', async function() {
        const target = document.getElementById(this.dataset.copyTarget);
        const status = document.getElementById(this.dataset.copyStatus);
        if (!target) return;

        window.clearTimeout(this.copyResetTimer);

        try {
          await copyText(target.textContent.trim());
          this.textContent = 'Copied';
          this.classList.add('is-copied');
          if (status) status.textContent = 'BibTeX copied to clipboard.';
        } catch (error) {
          this.textContent = 'Try again';
          this.classList.remove('is-copied');
          if (status) status.textContent = 'Unable to copy BibTeX.';
        }

        this.copyResetTimer = window.setTimeout(() => {
          this.textContent = 'Copy';
          this.classList.remove('is-copied');
        }, 1800);
      });
    });

    // Filter the blog archive by topic without leaving the page.
    const postItems = Array.from(document.querySelectorAll('#post-list .post-list-item'));
    const filterChips = Array.from(document.querySelectorAll('.filter-chip'));
    const postStatus = document.getElementById('post-filter-status');
    let activeTag = 'all';

    function filterPosts() {
      let visibleCount = 0;

      postItems.forEach(function(item) {
        const tags = (item.dataset.tags || '').toLowerCase().split(/\s+/);
        const isVisible = activeTag === 'all' || tags.includes(activeTag);
        item.hidden = !isVisible;
        visibleCount += isVisible ? 1 : 0;
      });

      if (postStatus) {
        postStatus.textContent = `${visibleCount} ${visibleCount === 1 ? 'post' : 'posts'}`;
      }
    }

    if (postItems.length) {
      filterChips.forEach(function(chip) {
        chip.addEventListener('click', function() {
          activeTag = (chip.dataset.tag || 'all').toLowerCase();
          filterChips.forEach(function(otherChip) {
            const isActive = otherChip === chip;
            otherChip.classList.toggle('is-active', isActive);
            otherChip.setAttribute('aria-pressed', String(isActive));
          });
          filterPosts();
        });
      });
      filterPosts();
    }

    // Expand or collapse all publication years at once.
    const publicationSections = Array.from(document.querySelectorAll('.year-section'));
    const expandPublications = document.getElementById('expand-publications');
    const collapsePublications = document.getElementById('collapse-publications');

    if (expandPublications && collapsePublications && publicationSections.length) {
      expandPublications.addEventListener('click', function() {
        publicationSections.forEach(function(section) {
          section.open = true;
        });
      });
      collapsePublications.addEventListener('click', function() {
        publicationSections.forEach(function(section) {
          section.open = false;
        });
      });
    }
  });
