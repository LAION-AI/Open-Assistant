# Node OS shim [![Build Status](https://secure.travis-ci.org/AdesisNetlife/node-os-shim.png?branch=master)][travis] [![NPM version](https://badge.fury.io/js/os-shim.png)][badge]

> Native OS module API shim for older node.js versions

## About

Node.js team froze the [OS module API][1] in 0.10.x version, however the API differs a bit in lower node.js versions

This shim just provides the missing OS module API that is available on latest node.js versions.
You can now use the `os` package in old node.js versions without fear.

It's based on the current node.js [implementations][2]

## Installation

```
$ npm install os-shim --save[-dev]
```

## Usage

You simply should use the `os-shim` module instead of the `os` native node.js module

```js
var os = require('os-shim')
os.tmpdir()
```
You can mutate the `os-shim` module object without worring about it can create side effects in the native `os` module object

## The missing API

The following API is missing in node.js `0.8.x` and lower versions

#### os.tmpdir()
Returns the operating system's default directory for temp files

#### os.endianness()
Returns the endianness of the CPU. Possible values are "BE" or "LE"

#### os.EOL
A constant defining the appropriate End-of-line marker for the operating system

#### os.platform()
Returns the operating system platform

#### os.arch()
Returns the operating system CPU architecture

## Contributing

Instead of a formal styleguide, take care to maintain the existing coding style.

Add unit tests for any new or changed functionality

### Development

Clone the repository
```shell
$ git clone https://github.com/adesisnetlife/node-os-shim.git && cd node-os-shim
```

Install dependencies
```shell
$ npm install
```

Run tests
```shell
$ make test
```

## Release History

- **0.1.1** `2013-12-11`
    - Add platform() and arch() methods (for Node.js 0.4.x)
- **0.1.0** `2013-12-11`
    - Initial release

## To Do

- Add `os.networkInterfaces()` shim method

Do you miss something? Open an issue or make a PR!

## Contributors

* [Tomas Aparicio](http://github.com/h2non)

## License

Copyright (c) 2013 Adesis Netlife S.L and contributors

Released under MIT license

[1]: http://nodejs.org/api/os.html
[2]: https://github.com/joyent/node/blob/master/lib/os.js
[travis]: http://travis-ci.org/AdesisNetlife/node-os-shim
[badge]: http://badge.fury.io/js/os-shim
