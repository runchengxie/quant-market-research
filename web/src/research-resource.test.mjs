import test from 'node:test';
import assert from 'node:assert/strict';

const resourceModule = await import('./lib/research-resource.ts').catch(error => {
  if (error.code === 'ERR_MODULE_NOT_FOUND') return {};
  throw error;
});
const { createResource, parseJsonResource, parseCsvResource } = resourceModule;
const deferred = () => { let resolve; const promise = new Promise(r => {resolve=r;}); return {promise,resolve}; };
const flush = async () => { for(let i=0;i<12;i++) await Promise.resolve(); };

test('resource loader exposes the request lifecycle contract', () => {
  assert.equal(typeof createResource, 'function');
});

test('optional null resource skips loading; separate successful resources survive another failure', async () => {
  assert.equal(typeof createResource, 'function');
  const absent = createResource(null,parseJsonResource);
  absent.load();
  assert.deepEqual(absent.getSnapshot(),{data:null,error:'',loading:false});
  const ready = createResource('/ready',parseJsonResource,async()=>new Response('{"ok":true}'));
  ready.load(); await flush();
  assert.deepEqual(ready.getSnapshot(),{data:{ok:true},error:'',loading:false});
  const failed = createResource('/bad',parseJsonResource,async()=>new Response('',{status:503}));
  failed.load(); await flush();
  assert.match(failed.getSnapshot().error,/503/);
  assert.deepEqual(ready.getSnapshot().data,{ok:true});
});

test('retry clears error, settles loading, and ignores an older response', async () => {
  assert.equal(typeof createResource, 'function');
  const old = deferred(); let attempt=0;
  const resource = createResource('/data',parseJsonResource,()=> ++attempt===1 ? old.promise : Promise.resolve(new Response('{"new":true}')));
  resource.load(); resource.load(); await flush();
  assert.deepEqual(resource.getSnapshot().data,{new:true});
  old.resolve(new Response('{"old":true}')); await flush();
  assert.deepEqual(resource.getSnapshot().data,{new:true});
  resource.cancel();
});

test('failure can recover and successful data is retained during refresh', async () => {
  assert.equal(typeof createResource, 'function');
  let attempt=0; const pending=deferred();
  const resource=createResource('/data',parseJsonResource,async()=> {
    attempt++;
    if(attempt===1) throw new Error('offline');
    if(attempt===2) return new Response('[1]');
    return pending.promise;
  });
  resource.load(); await flush();
  assert.match(resource.getSnapshot().error,/offline/);
  resource.load();
  assert.equal(resource.getSnapshot().error,'');
  assert.equal(resource.getSnapshot().loading,true);
  await flush();
  assert.deepEqual(resource.getSnapshot().data,[1]);
  resource.load();
  assert.deepEqual(resource.getSnapshot().data,[1]);
  resource.cancel();
});

test('hung fetch and hung response body both time out and abort even if transport ignores abort', async t => {
  assert.equal(typeof createResource, 'function');
  t.mock.timers.enable({apis:['setTimeout']});
  for(const hungBody of [false,true]) {
    let signal;
    const resource=createResource('/slow',parseJsonResource,async(_url,options)=> {
      signal=options.signal;
      return hungBody ? {ok:true,text:()=>new Promise(()=>{})} : new Promise(()=>{});
    });
    resource.load(); await flush();
    t.mock.timers.tick(15000); await flush();
    assert.equal(resource.getSnapshot().loading,false);
    assert.match(resource.getSnapshot().error,/超时|timed out/i);
    assert.equal(signal.aborted,true);
  }
});

test('cancel prevents stale completion notifications and aborts the old request', async () => {
  assert.equal(typeof createResource, 'function');
  const old=deferred(); let signal; let notices=0;
  const resource=createResource('/old',parseJsonResource,(_url,options)=>{signal=options.signal;return old.promise;});
  const unsubscribe=resource.subscribe(()=>notices++);
  resource.load(); resource.cancel(); const before=notices;
  old.resolve(new Response('123')); await flush();
  assert.equal(notices,before);
  assert.equal(signal.aborted,true);
  unsubscribe();
});

test('JSON validates syntax without imposing a domain schema', () => {
  assert.equal(typeof parseJsonResource, 'function');
  assert.deepEqual(parseJsonResource('{"arbitrary":[null,1]}'),{arbitrary:[null,1]});
  assert.equal(parseJsonResource('false'),false);
  assert.equal(parseJsonResource('null'),null);
  assert.throws(()=>parseJsonResource('<html>fallback</html>'));
  assert.throws(()=>parseJsonResource(''));
});

test('CSV accepts quoted fields, BOM, blanks and header-only data but rejects malformed structure', () => {
  assert.equal(typeof parseCsvResource, 'function');
  assert.deepEqual(parseCsvResource('\ufeffname,value\r\n"a,b",\r\n"two\nlines","say ""hi"""\n'),[{name:'a,b',value:''},{name:'two\nlines',value:'say "hi"'}]);
  assert.deepEqual(parseCsvResource('a,b\n'),[]);
  assert.deepEqual(parseCsvResource(''),[]);
  for(const text of ['a,b\n"unterminated,2','a,a\n1,2','a,b\n1,2,3','<html>fallback</html>','a,b\n1','a,b\nx"y,2']) assert.throws(()=>parseCsvResource(text),text);
});
