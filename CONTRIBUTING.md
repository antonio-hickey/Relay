# Contributing to Relay
First off thanks for helping with this project.

This project has many opportunities to contribute at any level. Every contribution is highly valued and no contribution is too small.

You do not need to write code to contribute to this project. Documentation, demos, and feature design advancements are a key part of this project's growth.

One of the best ways to begin contributing in a meaningful way is by helping find bugs and filing issues for them.

### Getting started
1. Follow the [installation guide](https://github.com/antonio-hickey/Relay/blob/main/README.md) in the `README.md`
3. Link your fork with the repository `git remote add upstream https://github.com/antonio-hickey/Relay.git`
4. That's it! You can now `git fetch upstream` and `git rebase [-i] upstream/rolling` to update your branches with the latest contributions.

### Cloning the repository
In the directory you want to save it run the command: `git clone https://github.com/antonio-hickey/Relay.git`

### Commit messages
- Commit header is limited to 72 characters.
- Commit body and footer is limited to 100 characters per line.

##### Commit header format:
```
<type>(<scope>?): <summary>
  │       │           │
  │       │           └─> Present tense.     'add something...'(O) vs 'added something...'(X)
  │       │               Imperative mood.   'move cursor to...'(O) vs 'moves cursor to...'(X)
  │       │               Not capitalized.
  │       │               No period at the end.
  │       │
  │       └─> Commit Scope is optional, but strongly recommended.
  │           Use lower case.
  │           'plugin', 'file', or 'directory' name is suggested, but not limited.
  │
  └─> Commit Type: build|ci|docs|feat|fix|perf|refactor|test
```

##### Commit Type Guideline
- build: changes that affect the build system or external dependencies (example scopes: npm, pip, rg)
- ci: changes to CI configuration files and scripts (example scopes: format, lint, issue_templates)
- docs: changes to the documentation only
- feat: new feature for the user
- fix: bug fix
- perf: performance improvement
- refactor: code change that neither fixes a bug nor adds a feature
- test: adding missing tests or correcting existing tests
- chore: all the rest, including version bump for plugins

### How to contribute
- Create a new branch: `git checkout -b YOUR_BRANCH_NAME`
- Add your changes: `git add PATH/TO/YOUR/CHANGES`
- Commit your changes: `git commit -m "TYPE_OF_CHANGE: VERY_SHORT_DESCRIPTION_OF_CHANGE"`
- Push to your branch: `git push origin YOUR_BRANCH_NAME`
