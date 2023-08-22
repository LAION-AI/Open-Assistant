## 1.0.2
- Check `/usr/local/bin/node` if we cannot find the binaries in the PATH.

## 1.0.1
- Corrected the `hook` file so it doesn't attempt to run **your** index.js but
  **ours** instead.

## 1.0
- Create symlinks instead of a copying the hook file so we can depend on
  modules.
- More readable output messages.
- Lookup git and npm using `which`.
- Allow nodejs, node and iojs to call the the hook.
- Refactored the way options can be passed in to pre-commit, we're now allowing
  objects.
- The refactor made it possible to test most of the internals so we now have
  90%+ coverage.
- And the list goes on. 

## 0.0.9
- Added missing uninstall hook to remove and restore old scripts.

## 0.0.8
- Added support for installing custom commit templates using `pre-commit.commit-template`

## 0.0.7
- Fixes regression introduced in 0.0.6

## 0.0.6
- Also silence `npm` output when the silent flag has been given.

## 0.0.5
- Allow silencing of the pre-commit output by setting a `precommit.silent: true`
  in your `package.json`

## 0.0.4
- Added a better error message when you fucked up your `package.json`.
- Only run tests if there are changes.
- Improved output formatting.

## 0.0.3
- Added compatibility for Node.js 0.6 by falling back to path.existsSync.

## 0.0.2
- Fixed a typo in the output, see #1.

## 0.0.1
- Use `spawn` instead of `exec` and give custom file descriptors. This way we
  can output color and have more control over the process.

## 0.0.0
- Initial release.
