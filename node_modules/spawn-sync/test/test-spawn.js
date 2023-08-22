'use strict';

process.stdin.pipe(require('fs').createWriteStream(__dirname + '/output.txt'));
process.stdout.write('output written');
process.stderr.write('error log exists');