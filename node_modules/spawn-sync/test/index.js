'use strict';

var assert = require('assert');
var vm = require('vm');
var fs = require('fs');
var path = require('path');
var sleep = require('try-thread-sleep');

function testSpawn(spawn) {
  var result = spawn("node", [__dirname + '/test-spawn.js'], {input: 'my-output'});
  assert(result.status === 0);
  assert(Buffer.isBuffer(result.stdout));
  assert(Buffer.isBuffer(result.stderr));
  assert(result.stdout.toString() === 'output written');
  assert(result.stderr.toString() === 'error log exists');
  assert(fs.readFileSync(__dirname + '/output.txt', 'utf8') === 'my-output');
  fs.unlinkSync(__dirname + '/output.txt');

  var result = spawn("node", [__dirname + '/test-spawn.js'], {
    input: 'my-output',
    encoding: 'utf-8'
  });
  assert(result.status === 0);
  assert(result.stdout === 'output written');
  assert(result.stderr === 'error log exists');
  assert.deepEqual(result.output, [null, 'output written', 'error log exists']);
  assert(fs.readFileSync(__dirname + '/output.txt', 'utf8') === 'my-output');
  fs.unlinkSync(__dirname + '/output.txt');

  var result = spawn("node", [__dirname + '/test-spawn-fail.js'], {input: 'my-output'});
  assert(result.status === 13);
  assert(Buffer.isBuffer(result.stdout));
  assert(Buffer.isBuffer(result.stderr));
  assert(result.stdout.toString() === 'output written');
  assert(result.stderr.toString() === 'error log exists');
  assert(fs.readFileSync(__dirname + '/output.txt', 'utf8') === 'my-output');
  fs.unlinkSync(__dirname + '/output.txt');

  var result = spawn("node", [__dirname + '/test-empty.js'], {input: 'my-output'});
  assert(result.status === 0);
  assert(Buffer.isBuffer(result.stdout));
  assert(Buffer.isBuffer(result.stderr));
  assert(result.stdout.toString() === '');
  assert(result.stderr.toString() === '');

  var result = spawn("node", [__dirname + '/test-empty.js'], { stdio: ['pipe', 'ignore', 'pipe']});
  assert(result.status === 0);
  assert(Buffer.isBuffer(result.stderr));
  assert(result.stdout == null);
  assert(result.stderr.toString() === '');

  var result = spawn("node", [__dirname + '/test-empty.js'], { stdio: ['pipe', 'pipe', 'ignore']});
  assert(result.status === 0);
  assert(Buffer.isBuffer(result.stdout));
  assert(result.stdout.toString() === '');
  assert(result.stderr == null);

  var result = spawn("node", [__dirname + '/test-empty.js'], { stdio: ['ignore', 'pipe', 'pipe']});
  assert(result.status === 0);
  assert(Buffer.isBuffer(result.stdout));
  assert(Buffer.isBuffer(result.stderr));
  assert(result.stdout.toString() === '');
  assert(result.stderr.toString() === '');

  // This suprisingly fails for the official API
  /*
  var start = Date.now();
  var result = spawn("node", [__dirname + '/test-spawn-timeout.js'], {timeout: 100});
  console.dir(result);
  var end = Date.now();
  assert((end - start) < 200);
  */

  console.log('test pass');
}

if (sleep.native) {
  console.log('Using native thread-sleep');
} else {
  console.log('Using busy waiting');
}
if (require('child_process').spawnSync) {
  console.log('# Test built in node API');
  testSpawn(require('child_process').spawnSync);
} else {
  console.log('# SKIP Test built in node API');
}
console.log('# Test fallback operation');
testSpawn(require('../lib/spawn-sync'));

console.log('All tests passed');
