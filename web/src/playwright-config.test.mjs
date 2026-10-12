import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

const configUrl = new URL('../playwright.config.ts', import.meta.url).href;

for (const [name, port, ci] of [
  ['default local port', undefined, undefined],
  ['custom local port', '54387', undefined],
  ['custom CI port', '54388', 'true'],
]) {
  test(`browser configuration uses ${name} and requires its own server`, () => {
    const env = { ...process.env };
    delete env.PORT;
    delete env.CI;
    delete env.NODE_TEST_CONTEXT;
    if (port !== undefined) env.PORT = port;
    if (ci !== undefined) env.CI = ci;
    const result = spawnSync(process.execPath, ['--import', 'tsx', '--input-type=module', '-e', `
      const { default: config } = await import(${JSON.stringify(configUrl)});
      console.log(JSON.stringify({
        baseURL: config.use.baseURL,
        serverUrl: config.webServer.url,
        reuseExistingServer: config.webServer.reuseExistingServer,
      }));
    `], { env, encoding: 'utf8' });
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr);
    const config = JSON.parse(result.stdout);
    const expectedUrl = `http://127.0.0.1:${port ?? '4321'}/quant-market-research/`;
    assert.equal(config.baseURL, expectedUrl);
    assert.equal(config.serverUrl, expectedUrl);
    assert.equal(config.reuseExistingServer, false);
  });
}
