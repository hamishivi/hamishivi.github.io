---
layout: post
title: A Quick Tip for brew cleanup
---

This is just a quick tip for anyone with errors happening whenever they run ```brew cleanup``` - based off [this thread on Github](https://github.com/Homebrew/legacy-homebrew/issues/44945). As a disclaimer, this isn't a global fix for all errors with ```brew cleanup``` - I wrote this on March 3rd 2020, so it may become outdated at some point too. However, I hope it is of use to someone!

If your error looks like this:
```
Error: undefined method `nonzero?' for nil:NilClass
Please report this bug:
  https://docs.brew.sh/Troubleshooting
/usr/local/Homebrew/Library/Homebrew/pkg_version.rb:39:in `<=>'
/usr/local/Homebrew/Library/Homebrew/formula.rb:541:in `=='
/usr/local/Homebrew/Library/Homebrew/formula.rb:541:in `prefix'
/usr/local/Homebrew/Library/Homebrew/formula.rb:519:in `installed_prefix'
/usr/local/Homebrew/Library/Homebrew/formula.rb:467:in `latest_version_installed?'
/usr/local/Homebrew/Library/Homebrew/formula.rb:1958:in `eligible_kegs_for_cleanup'
/usr/local/Homebrew/Library/Homebrew/cleanup.rb:214:in `cleanup_formula'
/usr/local/Homebrew/Library/Homebrew/cleanup.rb:168:in `block in clean!'
/usr/local/Homebrew/Library/Homebrew/cleanup.rb:167:in `each'
/usr/local/Homebrew/Library/Homebrew/cleanup.rb:167:in `clean!'
/usr/local/Homebrew/Library/Homebrew/cleanup.rb:162:in `periodic_clean!'
/usr/local/Homebrew/Library/Homebrew/cleanup.rb:145:in `install_formula_clean!'
/usr/local/Homebrew/Library/Homebrew/cmd/upgrade.rb:142:in `block in upgrade_formulae'
/usr/local/Homebrew/Library/Homebrew/cmd/upgrade.rb:138:in `each'
/usr/local/Homebrew/Library/Homebrew/cmd/upgrade.rb:138:in `upgrade_formulae'
/usr/local/Homebrew/Library/Homebrew/cmd/upgrade.rb:115:in `upgrade'
/usr/local/Homebrew/Library/Homebrew/brew.rb:103:in `<main>'
```

Then you likely have a formula causing the issue. To see what formulae brew is iterating through, find the ```cleanup_formula``` function in the ```Homebrew/cleanup.rb``` file (this file will appear in the stacktrace from the error, as above). This will have an argument that is called ```formula``` or ```f```. Simply place ```puts f``` at the start of the function (or wherever seems appropriate), and ```brew cleanup``` will now print every formula that it is checking for cleaning. The final formula name that prints will be the formula causing the error!

To fix, just uninstall the formula causing the error. It may be the case that the formula is just broken, in which case you'll need to either log a bug with the formula maintainer or fix it yourself. If not, a re-install should fix it.