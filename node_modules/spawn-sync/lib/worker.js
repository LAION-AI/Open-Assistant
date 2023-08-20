'use strict';

var cp = require('child_process');
var fs = require('fs');
var concat = require('concat-stream');
var JSON = require('./json-buffer');

var inputFile = process.argv[2];
var outputFile = process.argv[3];

var args = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
function output(result) {
  fs.writeFileSync(outputFile, JSON.stringify(result));
}

var child = cp.spawn.apply(cp, args);
var options = (args[2] && typeof args[2] === 'object') ?
                args[2] :
              (args[1] && typeof args[1] === 'object' && !Array.isArray(args[1])) ?
                args[1] :
                {};

var complete = false;
var stdout, stderr;
child.stdout && child.stdout.pipe(concat(function (buf) {
  stdout = buf.length ? buf : new Buffer(0);
}));
child.stderr && child.stderr.pipe(concat(function (buf) {
  stderr = buf.length ? buf : new Buffer(0);
}));
child.on('error', function (err) {
  output({pid: child.pid, error: err.message});
});
child.on('close', function (status, signal) {
  if (options.encoding && options.encoding !== 'buffer') {
    stdout = stdout.toString(options.encoding);
    stderr = stderr.toString(options.encoding);
  }
  output({
    pid: child.pid,
    output: [null, stdout, stderr],
    stdout: stdout,
    stderr: stderr,
    status: status,
    signal: signal
  });
});

if (options.timeout && typeof options.timeout === 'number') {
  setTimeout(function () {
    child.kill(options.killSignal || 'SIGTERM');
  }, options.timeout);
}
if (options.input && (typeof options.input === 'string' || Buffer.isBuffer(options.input))) {
  child.stdin.end(options.input);
}
