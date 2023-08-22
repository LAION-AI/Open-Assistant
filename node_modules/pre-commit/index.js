'use strict';

var spawn = require('cross-spawn')
  , which = require('which')
  , path = require('path')
  , util = require('util')
  , tty = require('tty');

/**
 * Representation of a hook runner.
 *
 * @constructor
 * @param {Function} fn Function to be called when we want to exit
 * @param {Object} options Optional configuration, primarily used for testing.
 * @api public
 */
function Hook(fn, options) {
  if (!this) return new Hook(fn, options);
  options = options || {};

  this.options = options;     // Used for testing only. Ignore this. Don't touch.
  this.config = {};           // pre-commit configuration from the `package.json`.
  this.json = {};             // Actual content of the `package.json`.
  this.npm = '';              // The location of the `npm` binary.
  this.git = '';              // The location of the `git` binary.
  this.root = '';             // The root location of the .git folder.
  this.status = '';           // Contents of the `git status`.
  this.exit = fn;             // Exit function.

  this.initialize();
}

/**
 * Boolean indicating if we're allowed to output progress information into the
 * terminal.
 *
 * @type {Boolean}
 * @public
 */
Object.defineProperty(Hook.prototype, 'silent', {
  get: function silent() {
    return !!this.config.silent;
  }
});

/**
 * Boolean indicating if we're allowed and capable of outputting colors into the
 * terminal.
 *
 * @type {Boolean}
 * @public
 */
Object.defineProperty(Hook.prototype, 'colors', {
  get: function colors() {
    return this.config.colors !== false && tty.isatty(process.stdout.fd);
  }
});

/**
 * Execute a binary.
 *
 * @param {String} bin Binary that needs to be executed
 * @param {Array} args Arguments for the binary
 * @returns {Object}
 * @api private
 */
Hook.prototype.exec = function exec(bin, args) {
  return spawn.sync(bin, args, {
    stdio: 'pipe'
  });
};

/**
 * Parse the package.json so we can create an normalize it's contents to
 * a usable configuration structure.
 *
 * @api private
 */
Hook.prototype.parse = function parse() {
  var pre = this.json['pre-commit'] || this.json.precommit
    , config = !Array.isArray(pre) && 'object' === typeof pre ? pre : {};

  ['silent', 'colors', 'template'].forEach(function each(flag) {
    var value;

    if (flag in config) value = config[flag];
    else if ('precommit.'+ flag in this.json) value = this.json['precommit.'+ flag];
    else if ('pre-commit.'+ flag in this.json) value = this.json['pre-commit.'+ flag];
    else return;

    config[flag] = value;
  }, this);

  //
  // The scripts we need to run can be set under the `run` property.
  //
  config.run = config.run || pre;

  if ('string' === typeof config.run) config.run = config.run.split(/[, ]+/);
  if (
       !Array.isArray(config.run)
    && this.json.scripts
    && this.json.scripts.test
    && this.json.scripts.test !== 'echo "Error: no test specified" && exit 1'
  ) {
    config.run = ['test'];
  }

  this.config = config;
};

/**
 * Write messages to the terminal, for feedback purposes.
 *
 * @param {Array} lines The messages that need to be written.
 * @param {Number} exit Exit code for the process.exit.
 * @api public
 */
Hook.prototype.log = function log(lines, exit) {
  if (!Array.isArray(lines)) lines = lines.split('\n');
  if ('number' !== typeof exit) exit = 1;

  var prefix = this.colors
  ? '\u001b[38;5;166mpre-commit:\u001b[39;49m '
  : 'pre-commit: ';

  lines.push('');     // Whitespace at the end of the log.
  lines.unshift('');  // Whitespace at the beginning.

  lines = lines.map(function map(line) {
    return prefix + line;
  });

  if (!this.silent) lines.forEach(function output(line) {
    if (exit) console.error(line);
    else console.log(line);
  });

  this.exit(exit, lines);
  return exit === 0;
};

/**
 * Initialize all the values of the constructor to see if we can run as an
 * pre-commit hook.
 *
 * @api private
 */
Hook.prototype.initialize = function initialize() {
  ['git', 'npm'].forEach(function each(binary) {
    try { this[binary] = which.sync(binary); }
    catch (e) {}
  }, this);

  //
  // in GUI clients node and npm are not in the PATH so get node binary PATH,
  // add it to the PATH list and try again.
  //
  if (!this.npm) {
    try {
      process.env.PATH += path.delimiter + path.dirname(process.env._);
      this.npm = which.sync('npm');
    } catch (e) {
      return this.log(this.format(Hook.log.binary, 'npm'), 0);
    }
  }

  //
  // Also bail out if we cannot find the git binary.
  //
  if (!this.git) return this.log(this.format(Hook.log.binary, 'git'), 0);

  this.root = this.exec(this.git, ['rev-parse', '--show-toplevel']);
  this.status = this.exec(this.git, ['status', '--porcelain']);

  if (this.status.code) return this.log(Hook.log.status, 0);
  if (this.root.code) return this.log(Hook.log.root, 0);

  this.status = this.status.stdout.toString().trim();
  this.root = this.root.stdout.toString().trim();

  try {
    this.json = require(path.join(this.root, 'package.json'));
    this.parse();
  } catch (e) { return this.log(this.format(Hook.log.json, e.message), 0); }

  //
  // We can only check for changes after we've parsed the package.json as it
  // contains information if we need to suppress the empty message or not.
  //
  if (!this.status.length && !this.options.ignorestatus) {
    return this.log(Hook.log.empty, 0);
  }

  //
  // If we have a git template we should configure it before checking for
  // scripts so it will still be applied even if we don't have anything to
  // execute.
  //
  if (this.config.template) {
    this.exec(this.git, ['config', 'commit.template', '"'+ this.config.template +'"']);
  }

  if (!this.config.run) return this.log(Hook.log.run, 0);
};

/**
 * Run the specified hooks.
 *
 * @api public
 */
Hook.prototype.run = function runner() {
  var hooked = this;

  (function again(scripts) {
    if (!scripts.length) return hooked.exit(0);

    var script = scripts.shift();

    //
    // There's a reason on why we're using an async `spawn` here instead of the
    // `shelljs.exec`. The sync `exec` is a hack that writes writes a file to
    // disk and they poll with sync fs calls to see for results. The problem is
    // that the way they capture the output which us using input redirection and
    // this doesn't have the required `isAtty` information that libraries use to
    // output colors resulting in script output that doesn't have any color.
    //
    spawn(hooked.npm, ['run', script, '--silent'], {
      env: process.env,
      cwd: hooked.root,
      stdio: [0, 1, 2]
    }).once('close', function closed(code) {
      if (code) return hooked.log(hooked.format(Hook.log.failure, script, code));

      again(scripts);
    });
  })(hooked.config.run.slice(0));
};

/**
 * Expose some of our internal tools so plugins can also re-use them for their
 * own processing.
 *
 * @type {Function}
 * @public
 */
Hook.prototype.format = util.format;

/**
 * The various of error and status messages that we can output.
 *
 * @type {Object}
 * @private
 */
Hook.log = {
  binary: [
    'Failed to locate the `%s` binary, make sure it\'s installed in your $PATH.',
    'Skipping the pre-commit hook.'
  ].join('\n'),

  status: [
    'Failed to retrieve the `git status` from the project.',
    'Skipping the pre-commit hook.'
  ].join('\n'),

  root: [
    'Failed to find the root of this git repository, cannot locate the `package.json`.',
    'Skipping the pre-commit hook.'
  ].join('\n'),

  empty: [
    'No changes detected.',
    'Skipping the pre-commit hook.'
  ].join('\n'),

  json: [
    'Received an error while parsing or locating the `package.json` file:',
    '',
    '  %s',
    '',
    'Skipping the pre-commit hook.'
  ].join('\n'),

  run: [
    'We have nothing pre-commit hooks to run. Either you\'re missing the `scripts`',
    'in your `package.json` or have configured pre-commit to run nothing.',
    'Skipping the pre-commit hook.'
  ].join('\n'),

  failure: [
    'We\'ve failed to pass the specified git pre-commit hooks as the `%s`',
    'hook returned an exit code (%d). If you\'re feeling adventurous you can',
    'skip the git pre-commit hooks by adding the following flags to your commit:',
    '',
    '  git commit -n (or --no-verify)',
    '',
    'This is ill-advised since the commit is broken.'
  ].join('\n')
};

//
// Expose the Hook instance so we can use it for testing purposes.
//
module.exports = Hook;

//
// Run directly if we're required executed directly through the CLI
//
if (module !== require.main) return;

var hook = new Hook(function cli(code) {
  process.exit(code);
});

hook.run();
