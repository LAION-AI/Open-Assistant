# spawn-sync

Polyfill for `child_process.spawnSync`.

On iojs and node >= 0.12 it will just export the built in `child_process.spawnSync`. On platforms that support compiling native modules it uses the [thread-sleep](https://github.com/ForbesLindesay/thread-sleep) module to wait for an output file to exist in a tight loop.  In this way it gains excellent cross platform support, but don't expect it to be efficient on all platforms.

[![Tests Status](https://img.shields.io/travis/ForbesLindesay/spawn-sync/master.svg)](https://travis-ci.org/ForbesLindesay/spawn-sync)
[![Dependency Status](https://img.shields.io/david/ForbesLindesay/spawn-sync.svg)](https://david-dm.org/ForbesLindesay/spawn-sync)
[![NPM version](https://img.shields.io/npm/v/spawn-sync.svg)](https://www.npmjs.com/package/spawn-sync)

## Installation

    npm install spawn-sync

If this fails, you can try one of the following things:

1. Some package managers made a stupid decision to rename the `node` executable to `nodejs` for their platform.  This breaks compatibility with lots of modules.  If you normally use `nodejs` instead of `node`, you should check out http://stackoverflow.com/questions/18130164/nodejs-vs-node-on-ubuntu-12-04 for possible fixes.

2. You can install using `--unsafe-perm`, which will fix any permissions issues.

    npm install --unsafe-perm spawn-sync

3. You can install using `--ignore-scripts`, which will skip native compilation.  You'll get a warning if you try to require the module, but everything should still work.

    npm install --ignore-scripts spawn-sync

4. You can try [updating npm](https://docs.npmjs.com/getting-started/installing-node), since this seems to fail on some older versions of npm:

    sudo npm install npm -g

5. You can upgrade to the latest version of node or iojs.  This will make native compilation unnecessary.  You can then use `--ignore-scripts` without getting a warning if you still have trouble.

## Usage

```js
var spawnSync = require('spawn-sync');

var result = spawnSync('node',
                       ['filename.js'],
                       {input: 'write this to stdin'});

if (result.status !== 0) {
  process.stderr.write(result.stderr);
  process.exit(result.status);
} else {
  process.stdout.write(result.stdout);
  process.stderr.write(result.stderr);
}
```

## License

  MIT
