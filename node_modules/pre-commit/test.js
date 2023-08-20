/* istanbul ignore next */
describe('pre-commit', function () {
  'use strict';

  var assume = require('assume')
    , Hook = require('./');

  it('is exported as a function', function () {
    assume(Hook).is.a('function');
  });

  it('can be initialized without a `new` keyword', function () {
    var hook = Hook(function () {}, {
      ignorestatus: true
    });

    assume(hook).is.instanceOf(Hook);
    assume(hook.parse).is.a('function');
  });

  describe('#parse', function () {
    var hook;

    beforeEach(function () {
      hook = new Hook(function () {}, {
        ignorestatus: true
      });
    });

    it('extracts configuration values from precommit.<flag>', function () {
      hook.json = {
        'precommit.silent': true
      };

      assume(hook.silent).is.false();

      hook.parse();

      assume(hook.config.silent).is.true();
      assume(hook.silent).is.true();
    });

    it('extracts configuration values from pre-commit.<flag>', function () {
      hook.json = {
        'pre-commit.silent': true,
        'pre-commit.colors': false
      };

      assume(hook.silent).is.false();
      assume(hook.colors).is.true();

      hook.parse();

      assume(hook.config.silent).is.true();
      assume(hook.silent).is.true();
      assume(hook.colors).is.false();
    });

    it('normalizes the `pre-commit` to an array', function () {
      hook.json = {
        'pre-commit': 'test, cows, moo'
      };

      hook.parse();

      assume(hook.config.run).is.length(3);
      assume(hook.config.run).contains('test');
      assume(hook.config.run).contains('cows');
      assume(hook.config.run).contains('moo');
    });

    it('normalizes the `precommit` to an array', function () {
      hook.json = {
        'precommit': 'test, cows, moo'
      };

      hook.parse();

      assume(hook.config.run).is.length(3);
      assume(hook.config.run).contains('test');
      assume(hook.config.run).contains('cows');
      assume(hook.config.run).contains('moo');
    });

    it('allows `pre-commit` object based syntax', function () {
      hook.json = {
        'pre-commit': {
          run: 'test scripts go here',
          silent: true,
          colors: false
        }
      };

      hook.parse();

      assume(hook.config.run).is.length(4);
      assume(hook.config.run).contains('test');
      assume(hook.config.run).contains('scripts');
      assume(hook.config.run).contains('go');
      assume(hook.config.run).contains('here');
      assume(hook.silent).is.true();
      assume(hook.colors).is.false();
    });

    it('defaults to `test` if nothing is specified', function () {
      hook.json = {
        scripts: {
          test: 'mocha test.js'
        }
      };

      hook.parse();
      assume(hook.config.run).deep.equals(['test']);
    });

    it('ignores the default npm.script.test placeholder', function () {
      hook.json = {
        scripts: {
          test: 'echo "Error: no test specified" && exit 1'
        }
      };

      hook.parse();
      assume(hook.config.run).has.length(0);
    });
  });

  describe('#log', function () {
    it('prefixes the logs with `pre-commit`', function (next) {
      var hook = new Hook(function (code, lines) {
        assume(code).equals(1);
        assume(lines).is.a('array');

        assume(lines[0]).includes('pre-commit');
        assume(lines[1]).includes('pre-commit');
        assume(lines[1]).includes('foo');
        assume(lines).has.length(3);

        // color prefix check
        lines.forEach(function (line) {
          assume(line).contains('\u001b');
        });

        next();
      }, { ignorestatus: true });

      hook.config.silent = true;
      hook.log(['foo']);
    });

    it('allows for a custom error code', function (next) {
      var hook = new Hook(function (code, lines) {
        assume(code).equals(0);

        next();
      }, { ignorestatus: true });

      hook.config.silent = true;
      hook.log(['foo'], 0);
    });

    it('allows strings to be split \\n', function (next) {
      var hook = new Hook(function (code, lines) {
        assume(code).equals(0);

        assume(lines).has.length(4);
        assume(lines[1]).contains('foo');
        assume(lines[2]).contains('bar');

        next();
      }, { ignorestatus: true });

      hook.config.silent = true;
      hook.log('foo\nbar', 0);
    });

    it('does not output colors when configured to do so', function (next) {
      var hook = new Hook(function (code, lines) {
        assume(code).equals(0);

        lines.forEach(function (line) {
          assume(line).does.not.contain('\u001b');
        });

        next();
      }, { ignorestatus: true });

      hook.config.silent = true;
      hook.config.colors = false;

      hook.log('foo\nbar', 0);
    });

    it('output lines to stderr if error code 1', function (next) {
      var err = console.error;
      next = assume.plan(4, next);

      var hook = new Hook(function (code, lines) {
        console.error = err;
        next();
      }, { ignorestatus: true });

      console.error = function (line) {
        assume(line).contains('pre-commit: ');
      };

      hook.config.colors = false;
      hook.log('foo\nbar', 1);
    });

    it('output lines to stdout if error code 0', function (next) {
      var log = console.log;
      next = assume.plan(4, next);

      var hook = new Hook(function (code, lines) {
        console.log = log;
        next();
      }, { ignorestatus: true });

      console.log = function (line) {
        assume(line).contains('pre-commit: ');
      };

      hook.config.colors = false;
      hook.log('foo\nbar', 0);
    });
  });

  describe('#run', function () {
    it('runs the specified scripts and exit with 0 on no error', function (next) {
      var hook = new Hook(function (code, lines) {
        assume(code).equals(0);
        assume(lines).is.undefined();

        next();
      }, { ignorestatus: true });

      hook.config.run = ['example-pass'];
      hook.run();
    });

    it('runs the specified test and exits with 1 on error', function (next) {
      var hook = new Hook(function (code, lines) {
        assume(code).equals(1);

        assume(lines).is.a('array');
        assume(lines[1]).contains('`example-fail`');
        assume(lines[2]).contains('code (1)');

        next();
      }, { ignorestatus: true });

      hook.config.run = ['example-fail'];
      hook.run();
    });
  });
});
