'use strict';

process.stdin.pipe(require('fs').createWriteStream(__dirname + '/output.txt')).on('close', function () {
  setTimeout(function () {
    process.exit(13);
  }, 500);
});
process.stdout.write('output written');
process.stderr.write('error log exists');
